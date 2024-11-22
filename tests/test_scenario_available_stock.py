import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules



class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install stock_shipment_internal_load_available
        activate_modules('stock_shipment_internal_load_available')

        # Create company
        _ = create_company()
        company = get_company()

        ProductUom = Model.get('product.uom')
        ProductTemplate = Model.get('product.template')
        Location = Model.get('stock.location')
        ShipmentIn = Model.get('stock.shipment.in')
        ShipmentInternal = Model.get('stock.shipment.internal')
        Party = Model.get('party.party')

        supplier = Party(name='Supplier')
        supplier.save()

        # Create product
        unit, = ProductUom.find([('name', '=', "Unit")])
        template = ProductTemplate()
        template.name = "Product"
        template.default_uom = unit
        template.type = 'goods'
        template.list_price = Decimal('20')
        template.save()
        product, = template.products

        # Get stock locations::
        supplier_loc, = Location.find([('code', '=', 'SUP')])
        input_loc, = Location.find([('code', '=', 'IN')])
        storage_loc, = Location.find([('code', '=', 'STO')])

        # Create "storage 2" location
        storage_loc2 = Location(name='Storage 2', code='STO2')
        storage_loc2.save()


        # Create a shipment::

        shipment = ShipmentIn()
        shipment.supplier = supplier
        move = shipment.incoming_moves.new()
        move.product = product
        move.quantity = 10
        move.from_location = supplier_loc
        move.to_location = input_loc
        move.unit_price = Decimal('5')
        move.currency = company.currency
        shipment.save()
        shipment.click('receive')
        shipment.click('do')
        self.assertEqual(shipment.state, 'done')

        # create internal shipment frm input to storage location
        internal_shipment = ShipmentInternal()
        internal_shipment.from_location = storage_loc
        internal_shipment.to_location = storage_loc2
        self.assertEqual(internal_shipment.moves, [])
        internal_shipment.click('available_stock')
        self.assertEqual(len(internal_shipment.moves), 1)
        self.assertEqual(internal_shipment.moves[0].quantity, 10)
