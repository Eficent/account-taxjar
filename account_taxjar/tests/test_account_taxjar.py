# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# - (https://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from os.path import dirname, join

from vcr import VCR

logging.getLogger("vcr").setLevel(logging.WARNING)

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml'),
    filter_headers=['Authorization'],
    decode_compressed_response=True,
)

from odoo.tests import SavepointCase
from odoo.exceptions import ValidationError


class TestAccountTaxjar(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountTaxjar, cls).setUpClass()
        # Create Partner
        cls.state = cls.env.ref('base.state_us_6')
        cls.partner = cls.env['res.partner'].create({
            'name': 'City of Henderson',
            'street': '720-726 S Gunnison Ave',
            'city': 'Buena Vista',
            'zip': '81211',
            'state_id': cls.state.id,
        })
        # Update Company address
        cls.company = cls.env.ref('base.main_company')
        cls.company_res_partner = cls.env.ref('base.main_company').partner_id
        cls.company_res_partner.update(
            {
                'country_id': cls.state.country_id.id,
                'state_id': cls.state.id,
                'zip': '80538',
                'city': 'Loveland',
                'street': '626 W 66th St',
            }
        )
        # Prepare Tax Account
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test',
            'type': 'payable',
        })

        cls.account = cls.env['account.account'].create({
            'name': 'Test Sale Tax account',
            'code': 'TEST',
            'user_type_id': cls.account_type.id,
            'reconcile': True,
        })

        # Create TaxJar Configuration
        cls.taxjar = cls.env['base.account.taxjar'].create({
            'name': 'TaxJar',
            'taxjar_api_url': 'https://api.sandbox.taxjar.com',
            'taxjar_api_token': '',
            'taxable_account_id': cls.account.id
        })

        # Create Nexus
        cls.nexus = cls.env['account.fiscal.position'].create(
            {
                'name': 'Colorado',
                'state_ids': [(6, 0, [cls.state.id])],
                'country_id': cls.state.country_id.id,
                'auto_apply': True,
                'is_nexus': True,
                'sourcing_type': 'destination',
                'taxjar_id': cls.taxjar.id,
            }
        )
        cls.tax_category = cls.env['product.taxjar.category'].create(
            {
                'code': '31000',
                'description': 'Digital products transferred electronically',
                'name': 'Digital Goods',
                'taxjar_id': cls.taxjar.id
            }
        )
        cls.product_template = cls.env['product.template'].create({
            'name': 'Computer',
            'tax_code_id': cls.tax_category.id
        })
        cls.product_product = cls.env['product.product'].create({
            'name': 'Compute',
            'product_tmpl_id': cls.product_template.id
        })

        cls.account = cls.env.ref('account.demo_sale_of_land_account')

        cls.invoice = cls.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': cls.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': cls.partner.id,
            'account_id': cls.account.id,
            'fiscal_position_id': cls.nexus.id
        })
        cls.invoice_line = cls.env['account.invoice.line']
        cls.invoice_line1 = cls.invoice_line.create({
            'product_id': cls.product_product.id,
            'invoice_id': cls.invoice.id,
            'name': 'Compute Invoice Line',
            'price_unit': 200.0,
            'uom_id': cls.env.ref('product.product_uom_unit').id,
            'account_id': cls.account.id,
            'quantity': 1,
        })
    # TODO: Not working, unable to update id from request.
    def test_account_invoice_validate_on_update_taxjar_taxes(self):
        with recorder.use_cassette(cassette_library_dir=join(
                dirname(__file__), 'fixtures/cassettes'),
                replace_post_data_parameters=[('id', self.invoice_line1.id)]):
            self.invoice.action_invoice_open()
            self.assertEqual(self.invoice.amount_total, 215.8)

    @recorder.use_cassette()
    def test_sync_taxjar_tax_code(self):
        self.taxjar.sync_taxjar_tax_code()

    @recorder.use_cassette()
    def test_sync_taxjar_nexus_region(self):
        self.taxjar.sync_taxjar_nexus_region()
