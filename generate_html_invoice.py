# -*- coding: utf8 -*-
import csv
import sys
from decimal import Decimal
TWO = Decimal('0.01')

class Item:
    def __init__(self, display=None, quantity=None, price=None, 
            unit=None, comment=None, providor_zh=None):
        self.display = display
        self.quantity = quantity
        self.price = price
        self.unit = unit
        self.comment = comment
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
        else:
            i.price= [i.price]
            result[desc] = i
    for x in result.values():
        x.price = min(x.price)
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
            yield Item(
                    providor_zh=line[0].decode('utf8'),
                    display=line[1],
                    quantity=Decimal(line[2]),
                    unit=line[3],
                    price=Decimal(line[4]),
                    comment=line[6].decode('utf8'))

def item_to_csv(items):
    writer = csv.writer(sys.stdout)
    for i in items:
        writer.writerow([
            i.providor_zh.encode('utf8'), i.display, i.quantity, 
            i.unit, i.price, i.price*i.quantity, i.comment.encode('utf8')])


def item_to_html(items):
    items = list(items)
    total = 0
    for i in items:
        i.price = i.price.quantize(TWO)
        i.amount = (i.price * i.quantity).quantize(TWO)
        total += i.amount
    rate = Decimal('6.18')
    total_usd = (total / rate).quantize(TWO)
    from jinja2 import Template
    with open('html_inv_temp.html') as f:
        t = Template(f.read())
        print t.render(items=items, total_rmb=total, total_usd=total_usd, rate=rate)

    
def main():
    new_items = csvsource(sys.argv[1])
    item_to_html(new_items)


main()

