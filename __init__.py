# This file is part stock_internal_shipment_move module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import stock

def register():
    Pool.register(
        stock.ShipmentInternal,
        module='stock_shipment_internal_move', type_='model')
    Pool.register(
        module='stock_shipment_internal_move', type_='wizard')
    Pool.register(
        module='stock_shipment_internal_move', type_='report')
