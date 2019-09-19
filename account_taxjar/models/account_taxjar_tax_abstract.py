# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import api, models
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class AccountTaxJarTaxAbstract(models.AbstractModel):
    _name = 'account.taxjar.tax.abstract'
    _description = 'Account TaxJar Tax Abstract'
    _inherit = 'taxjar.tax.abstract'

    @staticmethod
    def _prepare_breakdown_rates(item, jur_state, county, city):
        precision = 3
        state_tax_amount = float_round(item['state_sales_tax_rate'] * 100,
                                       precision_digits=precision)
        county_tax_amount = float_round(item['county_tax_rate'] * 100,
                                        precision_digits=precision)
        city_tax_amount = float_round(item['city_tax_rate'] * 100,
                                      precision_digits=precision)
        special_tax_amount = float_round(item['special_tax_rate'] * 100,
                                         precision_digits=precision)
        res = []
        if state_tax_amount:
            res.append({
                'name': 'State Tax: %s: %.3f %%' % (
                    jur_state.code, state_tax_amount),
                'amount': state_tax_amount,
                'state_id': jur_state.id,
                'tax_group': 'account_taxjar.tax_group_taxjar_state'
            })
        else:
            res.append({
                'name': 'State Tax Exempt',
                'amount': 0.0,
                'tax_group': 'account_taxjar.tax_group_taxjar_state'
            })
        if county_tax_amount:
            res.append({
                'name': 'County Tax: %s/%s %.3f %%' % (
                    jur_state.code, county, county_tax_amount),
                'amount': county_tax_amount,
                'county': county,
                'state_id': jur_state.id,
                'tax_group': 'account_taxjar.tax_group_taxjar_county'
            })
        else:
            res.append({
                'name': 'County Tax Exempt',
                'amount': 0.0,
                'tax_group': 'account_taxjar.tax_group_taxjar_county'
            })
        if city_tax_amount:
            res.append({
                'name': 'City Tax: %s/%s/%s %.3f %%' % (
                    city, county, jur_state.code, city_tax_amount),
                'amount': city_tax_amount,
                'city': city,
                'county': county,
                'state_id': jur_state.id,
                'tax_group': 'account_taxjar.tax_group_taxjar_city'

            })
        else:
            res.append({
                'name': 'City Tax Exempt',
                'amount': 0.0,
                'tax_group': 'account_taxjar.tax_group_taxjar_city'
            })
        if special_tax_amount:
            res.append({
                'name': 'Special District Tax: %s/%s/%s %.3f %%' % (
                    city, county, jur_state.code, special_tax_amount),
                'amount': special_tax_amount,
                'city': city,
                'county': county,
                'state_id': jur_state.id,
                'tax_group': 'account_taxjar.tax_group_taxjar_district'
            })
        else:
            res.append({
                'name': 'District Tax Exempt',
                'amount': 0.0,
                'tax_group': 'account_taxjar.tax_group_taxjar_district'
            })
        return res

    @staticmethod
    def _set_tax_ids(line, taxes):
        line.invoice_line_tax_ids = [
            (6, 0, [x.id for x in taxes])]

    @api.model
    def _get_taxjar_tax(self, rate):
        domain = self.env['account.tax']._get_update_tax_domain(rate)
        taxjar_tax = self.env['account.tax'].search(domain, limit=1)
        if not taxjar_tax:
            taxable_account_id = self.fiscal_position_id.\
                taxjar_nexus_sourcing_id.taxable_account_id.id
            taxjar_tax = self.env['account.tax']._create_taxjar_tax(
                rate, taxable_account_id)
        return taxjar_tax
