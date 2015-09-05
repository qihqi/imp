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
