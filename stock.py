from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from trytond.model import ModelView


class ShipmentInternal(metaclass=PoolMeta):
    __name__ = 'stock.shipment.internal'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'available_stock': {
                'invisible': ~Eval('state').in_(['draft']),
                'depends': ['state'],
                },
            })

    @classmethod
    @ModelView.button
    def available_stock(cls, records):
        Product = Pool().get('product.product')
        Move = Pool().get('stock.move')
        for record in records:
            pbl = Product.products_by_location([record.from_location.id],
            with_childs=False, grouping=('product', 'lot'))
            print(pbl)
            to_save = []
            for item in pbl.items():
                if item[1] <= 0:
                    continue
                move = Move()
                move.product = item[0][1]
                move.lot = item[0][2]
                move.quantity = item[1]
                move.shipment = record
                move.unit = Product(item[0][1]).default_uom
                move.from_location = record.from_location
                move.to_location = record.to_location
                to_save.append(move)
            Move.save(to_save)