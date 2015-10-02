# -*- coding: utf8 -*-
import csv
import sys
from decimal import Decimal
from henry.importation.app import api
from henry.importation.models import *

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
        desc = (i.providor_zh, i.display, i.unit, i.price)
        if desc in result:  
            result[desc].comment.append(i.comment)
            result[desc].quantity += i.quantity
        else:
            i.comment = [i.comment]
            result[desc] = i
    for x in result.values():
        x.comment = ', '.join(x.comment)
    return sorted(result.values(), key=lambda i: (i.providor_zh, i.display))

def jin_to_kg(item):
    if item.unit == 'jin':
        item.unit = 'kg'
        item.quantity /= 2
        item.price *= 2
    if item.unit == 'cizhu':
        item.unit = 'kg'
        item.quantity = item.quantity / 67 * 30
        item.price = item.price * 67 / 30 
    return item


def dbsource(pid):
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
    # total = sum((price(i) * quantity(i) for i in items))
    # print '<p> Total %.2f </p>' % total
    print '<html><body>'
    print '<meta charset="UTF-8"> '
    print '<table>'
    for item in items:
        print '<tr>'
        print '<td>', item.providor_zh.encode('utf8'), '</td>'
        print '<td>', item.display, '</td>'
        print '<td>', item.quantity, '</td>'
        print '<td>', item.unit, '</td>'
        print '<td>', item.price, '</td>'
        print '<td>', item.price * item.quantity, '</td>'
        print '<td>', item.comment, '</td>'
        print '</tr>'
    print '</table>'
    print '</body></html>'

    
def main():
    new_items = csvsource(sys.argv[1])
    # new_items = map(jin_to_kg, new_items)
    # new_items = group_by_price(new_items)
    # item_to_html(new_items)
    item_to_csv(new_items)


main()

