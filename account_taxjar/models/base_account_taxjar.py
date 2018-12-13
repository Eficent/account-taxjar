# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .taxjar_request import TaxJarRequest


class BaseAccountTaxJar(models.Model):
    _name = 'base.account.taxjar'

    name = fields.Char()

    taxjar_api_url = fields.Char(
        string='TaxJar API URL',
    )
    taxjar_api_token = fields.Char(
        string='TaxJar API KEY',
    )

    taxable_account_id = fields.Many2one(
        'account.account', string='Taxable Account TaxJar',
        required=True
    )

    @api.multi
    def sync_taxjar_tax_code(self):
        tax_code = self.env['product.taxjar.category']
        request = TaxJarRequest(self.taxjar_api_url, self.taxjar_api_token)
        categories = request.get_product_tax_code()

        for category in categories.data[:]:
            exist_tax = tax_code.search(
                [('code', '=', category['product_tax_code'])], limit=1)
            if not exist_tax:
                tax_code.create({'code': category['product_tax_code'],
                                 'description': category['description'],
                                 'name': category['name'],
                                 'taxjar_id': self.id
                })
            else:
                if tax_code.code != category['product_tax_code'] or \
                        tax_code.description != category['description'] or \
                        tax_code.name != category['name']:
                    tax_code.update({'code': category['product_tax_code'],
                                     'description': category['description'],
                                     'name': category['name'],
                                     'taxjar_id': self.id})
        return True

    @api.multi
    def sync_taxjar_nexus_region(self):
        nexus_region = self.env['account.fiscal.position']
        state = self.env['res.country.state']
        request = TaxJarRequest(self.taxjar_api_url, self.taxjar_api_token)
        res = request.get_nexus_regions()

        for nexus in res.data:
            nexus_exist = nexus_region.search(
                    [('name', '=', 'TaxJar: %s' % nexus['region'])], limit=1)
            if not nexus_exist.id:
                nexus_state = state.search([
                    ('code', '=', nexus['region_code']),
                    ('country_id.code', '=', nexus['country_code'])], limit=1)
                if nexus_state:
                    nexus_region.create(
                        {
                            'name': nexus['region'],
                            'state_ids': [(6, 0, nexus_state.ids)],
                            'country_id': nexus_state.country_id.id,
                            'auto_apply': True,
                            'is_nexus': True,
                            'taxjar_id': self.id
                         }
                    )
                else:
                    raise ValidationError(_("No state found on system"))
        return True

