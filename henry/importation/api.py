from sqlalchemy.inspection import inspect
from .models import NPurchaseItem, NPurchase, NUniversalProduct

def make_serializable(names):
    class SerializableMixin(object):
        _name = names

        def __init__(self, **kwargs):
            self.merge_from(kwargs)

        def merge_from(self, obj):
            self.merge(obj, self, self._name)
            return self

        def merge_to(self, obj):
            self.merge(self, obj, self._name)
            return obj

        @classmethod
        def merge(cls, source, dest, keys):
            for key in keys:
                if hasattr(source, 'get'):
                    value = source.get(key, None)
                else:
                    value = getattr(source, key, None)
                setattr(dest, key, value)

        def serialize(self):
            return self._serialize_helper(self, self._name)

        @classmethod
        def deserialize(cls, dict_input):
            return cls().merge_from(dict_input)

        @staticmethod
        def _serialize_helper(obj, names):
            return {
                name: getattr(obj, name) for name in names if getattr(obj, name, None) is not None
            }
    return SerializableMixin

Purchase = make_serializable(['header', 'items'])
Header = make_serializable(inspect(NPurchase).columns.keys())

Item = make_serializable(['color', 'quantity', 'price_rmb', 'name_es', 
                          'name_zh', 'upi', 
                          'providor_zh', 'providor_item_id'])

def get_report(session, pkey):
    header = session.query(NPurchase).filter_by(uid=pkey).first()
    if header is None:
        return None
    items = list(session.query(
        NPurchaseItem.color, NPurchaseItem.quantity, NPurchaseItem.price_rmb, 
        NUniversalProduct.name_es, NUniversalProduct.name_zh, NUniversalProduct.providor_zh, 
        NUniversalProduct.providor_item_id, NUniversalProduct.upi).filter(
        NUniversalProduct.upi==NPurchaseItem.upi).filter(
        NPurchaseItem.purchase_id == pkey))
    return Purchase(
        header = Header.deserialize(header),
        items = map(Item.deserialize, items)
    )
