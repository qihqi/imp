# -*- coding: utf8 -*-
import csv
import sys
from decimal import Decimal
import re
from random import randint
TWO = Decimal('0.01')
reload(sys)
sys.setdefaultencoding('utf8')

def getint(x):
    return int(re.sub(r'[^\d]', '', x))

def int_or_none(x):
    try:
        return int(x)
    except:
        return None

class Item:
    def __init__(self, uid, order, display=None, quantity=None, price=None, 
            unit=None, size=None, comment=None, box=None, providor_zh=None):
        self.order = order
        self.uid= uid
        self.display = display
        self.quantity = quantity
        self.price = price
        self.unit = unit
        self.size = size
        self.comment = comment
        self.box = box
        self.providor_zh = providor_zh


def group_by_price(new_items):
    result = {}
    for i in new_items:
        # desc = (i.display, i.unit, i.price)
        desc = (i.providor_zh, i.display, i.unit, i.price)
        if desc in result:  
            result[desc].comment.append(i.comment)
            result[desc].quantity += i.quantity
        else:
            i.comment = [i.comment]
            result[desc] = i
    for x in result.values():
        x.comment = ', '.join(x.comment)
    return result.values()

def group_by_comment(items):
    result = {}
    for i in items:
        # desc = (i.display, i.unit, i.price)
        desc = i.comment
        if desc in result:  
            result[desc].price.append(i.price)
            result[desc].quantity += i.quantity
            result[desc].comment.append(i.comment)
        else:
            i.price = [i.price]
            i.comment = [i.comment]
            result[desc] = i
    for x in result.values():
        x.price = min(x.price)
        x.comment = ', '.join(x.comment)
    return result.values()


def jin_to_kg(item):
    mult = 1
    if item.unit == 'jin':
        item.unit = 'kg'
        mult = 2
    if item.unit == 'cizhu':
        item.unit = 'kg'
        mult = Decimal(67) / 30
    if item.unit == 'cen':
        item.unit = 'ciento'
        mult = 100
    if item.unit == '-50y':
        item.unit = 'rollo de 50 yardas'
        mult = 50 
    if item.unit == '-1000ge':
        item.unit = 'mil'
        mult = 1000 
    if item.unit == '-15y':
        item.unit = 'paquete de 15 yardas'
        mult = 15 
    if item.unit == '-100y':
        item.unit = 'rollos de 100 yardas'
        mult = 100 
    if item.unit == 'julia':
        item.unit = 'kg'
        mult = Decimal(28000) / 270
    if item.unit == 'wbao':
        item.unit = 'kg'
        mult = Decimal(1414) / 450
    if item.unit == 'leiyu':
        item.unit = 'kg'
        mult = Decimal(235) / Decimal('147.5')
    if item.unit == 'zhuoxin':
        item.unit = 'kg'
        mult = Decimal(50902) / 120
    if item.unit == '-12ge':
        item.unit = 'dozen'
        mult = 12
    if item.unit.isdigit():
        item.unit = 'paquete de ' + item.unit

    item.quantity /= mult
    item.price *= mult
    return item

def package(item):
    if item.unit.startswith('-'):
        cant = int(item.unit[1:-1])
        item.unit = 'paquete de {} tiras'.format(cant)
        item.quantity /= cant
        item.price *= cant 
    return item


def dbsource(pid):
    from henry.importation.app import api
    from henry.importation.models import (NDeclaredGood, NUniversalProduct,
            NPurchaseItem)
    session = api.sessionmaker()
    declared = {u.uid: u for u in session.query(NDeclaredGood)}
    prods = {u.upi: u for u in session.query(NUniversalProduct)}
    items = list(session.query(NPurchaseItem).filter_by(purchase_id=pid)) 

    def dname(item):
        decl = declared.get(prods[item.upi].declaring_id)
        if decl is None:
            print >>sys.stderr, 'not found decl', item.upi 
            return ''
        return decl.display_name.encode('utf8')

    def unit(item):
        p = prods[item.upi]
        return prods[item.upi].unit.encode('utf8')

    def realname(item):
        p = prods[item.upi]
        return '{}-{}'.format(p.providor_zh.encode('utf8'), 
                              p.name_zh.encode('utf8'))

    def quantity(item):
        p = prods[item.upi]
        return item.quantity

    def price(item):
        p = prods[item.upi]
        return item.price_rmb / 4

    def prov(item):
        return prods[item.upi].providor_zh.encode('utf8')

    def make_item(item):
        return Item(
                uid='',
                order='',
                display=dname(item),
                comment=realname(item),
                price=price(item),
                quantity=quantity(item),
                unit=unit(item),
                providor_zh=prov(item))

    return map(make_item, items)


def csvsource(path):
    with open(path) as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for line in reader:
            order, uid, providor_zh, display, quantity, unit, size, price, _, box, comment = line
            providor_zh = providor_zh.decode('utf8')
            quantity = Decimal(quantity)
            price = Decimal(price)
            box = int_or_none(box)
            comment = comment.decode('utf8')
            yield Item(
                    uid=uid,
                    order=order,
                    providor_zh=providor_zh,
                    display=display,
                    quantity=quantity,
                    unit=unit,
                    size=size,
                    price=price,
                    box=box,
                    comment=comment)

def item_to_csv(items):
    writer = csv.writer(sys.stdout)
    for i in items:
        writer.writerow([
            i.order, i.uid, i.providor_zh.encode('utf8'), i.display, i.quantity, 
            i.unit, i.size, i.price, i.price*i.quantity, i.box, i.comment.encode('utf8')])

def item_to_price_list(items):
    writer = csv.writer(sys.stdout)
    for i in items:
        try:
            comment = i.comment.split('-')[1]
            comment = comment.split(',')[0]
            writer.writerow([
                comment, i.display,  
                i.unit, i.price])
        except IndexError:
            pass

def smallcomment(i):
    try:
        i.comment = i.comment.split('-')[1]
        i.comment = i.comment.split(',')[0]
    except:
        pass
    return i

def normalize_items(items):
    for i in items:
        i.price = i.price.quantize(TWO)
        i.amount = (i.price * i.quantity).quantize(TWO)
        yield i

def item_to_csv_real(items):
    writer = csv.writer(sys.stdout)
    for i in items:
        writer.writerow([
            i.providor_zh.encode('utf8'), i.display, i.comment.encode('utf8'), i.quantity, 
            i.unit, i.box ])

def item_to_html(items, ofile=sys.stdout):
    rate = Decimal('6.18')
    total = 0 #sum((i.amount for i in items))
    total_usd = ( total / rate).quantize(TWO)
    from jinja2 import Template
    with open('html_inv_temp.html') as f:
        t = Template(f.read())
        ofile.write(t.render(items=items, total_rmb=total, total_usd=total_usd, rate=rate))
        ofile.write('\n')

class Meta(object):
    pass

def item_to_packing_list(items, ofile=sys.stdout):
    from jinja2 import Template
    groups = []
    sub = None
    for i in items:
        if i.box:
            if sub:
                groups.append(sub)
            sub = Meta()
            sub.box = i.box
            sub.items = []
        sub.items.append(i)
    groups.append(sub)
    for g in groups:
        if g.items[0].unit == 'kg':
            g.weight = sum((x.quantity for x in g.items))
        else:
            g.weight = (g.box or 0) * 30
    boxes = sum((i.box for i in groups if i.box is not None))
    weights = sum((i.weight for i in groups if i.weight is not None))

    with open('html_plist_temp2.html') as f:
        t = Template(f.read())
        ofile.write(t.render(items=groups, boxes=boxes, weight=weights))
        ofile.write('\n')

def change_price(item):
    item.price *= ( Decimal(4) / Decimal('3.5'))
    return item

# return list of list of items, representing what goes in each inv
# prices changed to usd with markup
def split_invoices(items, total_num):
    current_num = 0
    total_cant = [item.quantity for item in items]
    for i in range(total_num):
        next_set = [] 
        for i, item in enumerate(items):
            target = item.quantity / total_num + randint(-2, 2)
            if target >= total_cant[i]:
                target = total_cant[i]
            if i == total_num - 1:
                target = total_cant[i]
            total_cant[i] -= target
            new_item = Item('','')
            for x, y in item.__dict__.items():
                setattr(new_item, x, y)
            new_item.quantity = target
            next_set.append(new_item)
        yield next_set
    

    
def main():
    new_items = csvsource(sys.argv[1])
    # new_items = dbsource(19)
    item_to_csv(new_items) 

#    for i, inv in enumerate(split_invoices(new_items, 12)):
#        print 'INV NUMBER', i
#        print (len(group_by_price(inv)))
#        print 'total', sum((x.quantity * x.price for x in inv))
#        print '\n\n'




main()

