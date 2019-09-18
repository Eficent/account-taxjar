# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = ['account.tax', 'taxjar.breakdown.tax']
    _description = 'Add address info of tax collections'

    @staticmethod
    def _get_update_tax_domain(tax):
        city = tax.get('city', False)
        county = tax.get('county', False)
        state_id = tax.get('state_id', False)
        amount = tax.get('amount', 0.0)
        name = tax.get('name', '')
        domain = [('name', '=', name),
                  ('state_id', '=', state_id),
                  ('amount', '=', amount),
                  ('amount_type', '=', 'percent'),
                  ('type_tax_use', '=', 'sale'),
                  ('city', '=', city),
                  ('county', '=', county),
                  ]
        # TODO: add account_id to domain with taxable
        return domain

    def _create_taxjar_tax(self, rate, taxable_account_id):
        values = {
            'name': rate['name'],
            'amount': rate['amount'],
            'amount_type': 'percent',
            'type_tax_use': 'sale',  # TODO: See purchase side
            'description': rate['name'],  # TODO: Add Description TIMESTAMP
            'account_id': taxable_account_id,
            'refund_account_id': taxable_account_id,
            'state_id': rate['state_id'] if 'state_id' in rate else False,
            'city': rate['city'] if 'city' in rate else False,
            'county': rate['county'] if 'county' in rate else False,
            'tax_group_id': self.env.ref(rate['tax_group']).id
        }
        taxjar_tax = self.create(values)
        return taxjar_tax
