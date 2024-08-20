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
    def available_stock(cls, shipments):
        Product = Pool().get('product.product')
        Move = Pool().get('stock.move')
        to_save = []
        for shipment in shipments:
            pbl = Product.products_by_location([shipment.from_location.id],
                with_childs=False, grouping=('product', 'lot'))
            for key, value in pbl.items():
                if value <= 0:
                    continue
                move = Move()
                move.product = key[1]
                move.lot = key[2]
                move.quantity = value
                move.shipment = shipment
                move.unit = Product(key[1]).default_uom
                move.from_location = shipment.from_location
                move.to_location = shipment.to_location
                to_save.append(move)
        Move.save(to_save)
