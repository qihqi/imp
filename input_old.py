from henry.importation.app import api
from henry.importation.models import NUniversalProduct, NPurchaseItem
import csv
import sys
import re
from decimal import Decimal
from henry.helpers import parse_decimal



def main():
    session = api.sessionmaker()
    with open(sys.argv[1]) as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for line in reader:
            if not line[0].strip():
                continue
            providor = line[0].decode('utf8')
            name_zh = line[1].decode('utf8')

            prod = session.query(NUniversalProduct).filter_by(
                    providor_zh=providor, name_zh=name_zh).first()
            if prod is None:
                prod = NUniversalProduct(
                    name_zh=name_zh, providor_zh=providor)
                session.add(prod)
                session.flush()
                print 'prod added'

            upi = prod.upi
            quantity = parse_decimal(line[2].decode('utf8'))
            price = parse_decimal(line[3].decode('utf8'))

            item = NPurchaseItem(
                upi=upi,
                purchase_id=None,
                color=None,
                quantity=quantity,
                price_rmb=price)
            session.add(item)
            print 'item added'
            session.flush()
    session.commit()
main()
