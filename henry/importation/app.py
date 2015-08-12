# -*- coding: utf8 -*-
import csv
import decimal
from bottle import Bottle, request, static_file, JSONPlugin
import re
import bottle
import sys
from decimal import Decimal
from .bottlerest import DBApi, RestApiApp
from .models import NUniversalProduct, NPurchase, NPurchaseItem, Base, NDeclaredGood
from sqlalchemy import create_engine
import json

class ModelEncoder(json.JSONEncoder):
    def __init__(self, use_int_repr=False, decimal_places=2, *args, **kwargs):
        super(ModelEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super(ModelEncoder, self).default(obj)

def json_dumps(x):
    return json.dumps(x, cls=ModelEncoder)


CONN_STRING = 'mysql+mysqldb://root:wolverineaccess@localhost/import?charset=utf8'
engine = create_engine(CONN_STRING)
app = Bottle(autojson=False)

app.install(JSONPlugin(json_dumps=json_dumps))
api = RestApiApp(engine, app, encoder=ModelEncoder)
api.bind_api('/importapi/prod', NUniversalProduct)
api.bind_api('/importapi/purchaseheader', NPurchase)
api.bind_api('/importapi/purchaseitem', NPurchaseItem)
api.bind_api('/importapi/declaredgood', NDeclaredGood)

prodapi = api.getapi(NUniversalProduct)

@app.get('/app/purchase/<purchase_id>')
def get_purchase_full(purchase_id):
    obj = {}
    obj['header'] = purchase 
    


@app.get('/<path:path>')
def static_files(path):
    return static_file(path, root='static')


@app.get('/importapi/purchase/pid')
def get_purchase(pid):
    thing = get_purchase(api.sessionmaker, pid)
    print thing.deserialize()
    return thing.deserialize()


def parse_decimal(x):
    x = x.encode('utf8')
    print 'before x ', x
    x = re.sub(r'[^\d\.]', '', x)
    print x
    return Decimal(x)

if __name__ == '__main__':
    bottle.run(app)
    sys.exit(0)
    Base.metadata.create_all(engine)
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
