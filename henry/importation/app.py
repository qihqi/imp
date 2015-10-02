# -*- coding: utf8 -*-
import datetime
import csv
import decimal
from bottle import Bottle, request, static_file, JSONPlugin
import re
import bottle
import sys
from decimal import Decimal
from .bottlerest import DBApi, RestApiApp
from .models import NUniversalProduct, NPurchase, NPurchaseItem, Base, NDeclaredGood
from .api import get_report
from sqlalchemy import create_engine
from henry.constants import CONN_STRING
import json

class ModelEncoder(json.JSONEncoder):
    def __init__(self, use_int_repr=False, decimal_places=2, *args, **kwargs):
        super(ModelEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'serialize'):
            return obj.serialize()
        return super(ModelEncoder, self).default(obj)

def json_dumps(x):
    return json.dumps(x, cls=ModelEncoder)


engine = create_engine(CONN_STRING)
app = Bottle(autojson=False)

app.install(JSONPlugin(json_dumps=json_dumps))
api = RestApiApp(engine, app, encoder=ModelEncoder)
api.bind_api('/importapi/prod', NUniversalProduct)
api.bind_api('/importapi/purchaseheader', NPurchase)
api.bind_api('/importapi/purchaseitem', NPurchaseItem)
api.bind_api('/importapi/declaredgood', NDeclaredGood)

prodapi = api.getapi(NUniversalProduct)

@app.get('/importapi/purchase/<pid>')
def get_purchase(pid):
    session = api.sessionmaker()
    thing = get_report(session, pid)
    print thing.serialize()
    return thing.serialize()


@app.post('/importapi/purchase')
def save_purchase():
    session = api.sessionmaker()
    rows = json.loads(request.body.read())

    purchase = NPurchase()
    session.add(purchase)
    session.flush()
    def make_item(r):
        return NPurchaseItem(
            upi=r['prod']['upi'],
            quantity=Decimal(r['cant']),
            price_rmb=Decimal(r['price']),
            purchase_id = purchase.uid) 
    items = map(make_item, rows)
    total = sum((r.price_rmb * r.quantity for r in items))
    purchase.timestamp = datetime.datetime.now()
    purchase.total_rmb = total

    map(session.add, items)
    session.commit()
    return {'uid': purchase.uid}


@app.get('/importapi/purchaseitem2/<uid>')
def get_purchase(uid):
    session = api.sessionmaker()
    items = session.query(NPurchaseItem, NUniversalProduct
            ).filter(NPurchaseItem.upi == NUniversalProduct.upi).filter_by(purchase_id=uid)
    def make_item(r):
        item, prod = r
        return {
                'prod': {
                    'upi': prod.upi,
                    'name_zh': prod.name_zh,
                    'name_es': prod.name_es,
                    'providor_zh': prod.providor_zh,
                    'providor_item_id': prod.providor_item_id,
                },
                'cant': item.quantity,
                'price': item.price_rmb
            }
    items = map(make_item, items)
    return {'result': items}


@app.get('/<path:path>')
def static_files(path):
    return static_file(path, root='static')


def parse_decimal(x):
    x = re.sub(r'[^\d\.]', '', x)
    print x
    return Decimal(x)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    bottle.run(app)
    sys.exit(0)
    session = api.sessionmaker()
    prodapi = api.getapi(NUniversalProduct)
    with open(sys.argv[1]) as f:
        rows = csv.reader(f, delimiter=',', quotechar='"')
        for r in rows:
            item = NPurchaseItem(
                upi=prodapi.search(session, providor_item_id=r[2])[0]['upi'],
                color=r[3] + r[5],
                quantity=parse_decimal(r[7]),
                price_rmb=parse_decimal(r[8])
            )
            session.add(item)

        session.commit()
        session.close()
