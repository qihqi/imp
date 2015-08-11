# -*- coding: utf8 -*-
import csv
from bottle import Bottle, request, static_file
import re
import bottle
import sys
from decimal import Decimal
from .bottlerest import DBApi, RestApiApp
from .models import NUniversalProduct, NPurchase, NPurchaseItem, Base, NDeclaredGood
from sqlalchemy import create_engine

CONN_STRING = 'sqlite:///test.db'
engine = create_engine(CONN_STRING)
app = Bottle()
api = RestApiApp(engine, app)
api.bind_api('/importapi/prod', NUniversalProduct)
api.bind_api('/importapi/purchase', NPurchase)
api.bind_api('/importapi/purchaseitem', NPurchaseItem)
api.bind_api('/importapi/declaredgood', NDeclaredGood)

prodapi = api.getapi(NUniversalProduct)


@app.get('/<path:path>')
def static_files(path):
    return static_file(path, root='static')

@app.get('/import/prod')
@app.get('/import/prod/<pid>')
def create_or_edit_prod(pid=None):
    if pid is not None:
        proddict = api.getapi(NUniversalProduct).get(pid)
    else:
        proddict= prodapi.obj_to_dict(None, excludenone=False)
    temp = jinja_env.get_template('quickform.html')
    return temp.render(obj=proddict, action='post', method=request.url)


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
