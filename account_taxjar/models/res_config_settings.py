
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .taxjar_request import TaxjarRequest


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    taxjar_api_url = fields.Char(
        string='Taxjar API URL',
        default='',
        config_parameter='account_taxjar.taxjar_api_url'
    )
    taxjar_api_key = fields.Char(
        string='Taxjar API KEY',
        default='',
        config_parameter='account_taxjar.taxjar_api_key'
    )
    tax_code_id = fields.Many2one(
        related='company_id.tax_code_id',
        string="Default Product Tax Code",
        readonly=False
    )

    @api.multi
    def sync_taxjar_tax_code(self):
        tax_code = self.env['product.tax.code']
        request = TaxjarRequest(self.taxjar_api_url, self.taxjar_api_key)
        categories = request.get_product_tax_code()

        for category in categories.data[:]:
            if not tax_code.search(
                    [('code', '=', category['product_tax_code'])], limit=1):
                tax_code.create({'code': category['product_tax_code'],
                                 'description': category['description'],
                                 'name': category['name']})
        # if not self.env.user.company_id.tax_code_id:
        #     self.env.company_id.tic_category_id = tax_code.search(
        #         [('code', '=', 99999)], limit=1)
        return True

    @api.multi
    def sync_taxjar_nexus_region(self):
        nexus_region = self.env['account.fiscal.position']
        state = self.env['res.country.state']
        request = TaxjarRequest(self.taxjar_api_url, self.taxjar_api_key)
        res = request.get_nexus_regions()

        for nexus in res.data[:]:
            if not nexus_region.search(
                    [('state_ids.code', '=', nexus['region_code']),
                     ('state_ids.country_id.code', '=', nexus['country_code'])],
                    limit=1):
                nexus_state = state.search([('code', '=', nexus['region_code']),
                              ('country_id.code', '=', nexus['country_code'])],
                             limit=1)
                if nexus_state:
                    nexus_region.create(
                        {
                            'name': 'Taxjar Nexus: %s' % nexus['product_tax_code'],
                            'state_ids': state.id,
                            'country_id': state.country_id
                         }
                    )
                else:
                    raise ValidationError("No state found on system")
        return True


