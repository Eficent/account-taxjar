# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError

from odoo.addons.account_taxjar.models.taxjar_request import TaxJarRequest


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # # Disable sales order taxes on confirm
    # @api.multi
    # def action_confirm(self):
    #     if self.fiscal_position_id.is_nexus:
    #         self.prepare_taxes_on_order()
    #     return super(SaleOrder, self).action_confirm()

    def _get_nexus(self):
        return self.fiscal_position_id

    def _get_partner(self):
        return self.partner_id

    def _get_lines(self):
        lines = []
        for line in self.order_line:
            lines.append(line)
        return lines

    def _get_jurisdiction_state(self, jurisdiction):
        state_id = self.env['res.country.state'].search([
            ('code', '=', jurisdiction['state']),
            ('country_id.code', '=', jurisdiction['country'])
        ])
        return state_id

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

    def update_tax(self, tax, taxable_account_id):
        city = tax['city'] if 'city' in tax else False
        county = tax['county'] if 'county' in tax else False
        state_id = tax['state_id'] if 'state_id' in tax else False
        account_tax = self.env['account.tax']
        amount = tax['amount']
        name = tax['name']
        tax_group = tax['tax_group']
        domain = [('name', '=', name),
                  ('state_id', '=', state_id),
                  ('amount', '=', amount),
                  ('amount_type', '=', 'percent'),
                  ('type_tax_use', '=', 'sale'),
                  ('city', '=', city),
                  ('county', '=', county),
                  ('account_id', '=', taxable_account_id)]

        tax = account_tax.sudo().search(domain, limit=1)
        if not tax:
            tax_dict = {
                'name': name,
                'amount': amount,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'description': name,
                'account_id': taxable_account_id,
                'state_id': state_id,
                'city': city,
                'county': county,
                'tax_group_id': self.env.ref(tax_group).id
            }
            tax = account_tax.sudo().create(tax_dict)
        return tax

    # TODO: Split functions and refactor duplicities
    @api.multi
    def prepare_taxes_on_order(self):
        company = self.company_id or self.env.user.company_id
        partner = self._get_partner()
        nexus = self._get_nexus()
        lines = self._get_lines()
        if not company or not partner or not nexus or not lines:
            raise ValidationError(_("Request cannot be executed due to: "
                                    "company, partner, nexus or invoice lines"
                                    "don't exist"))

        taxjar_id = self.fiscal_position_id.taxjar_id
        taxable_account_id = taxjar_id.taxable_account_id.id
        api_url = taxjar_id.taxjar_api_url
        api_token = taxjar_id.taxjar_api_token
        request = TaxJarRequest(api_url, api_token)

        res = request.get_rate(lines, partner, company, nexus)

        items = res['breakdown']['line_items'] if 'breakdown' in res else {}
        jurisdiction = res['jurisdictions'] if 'jurisdictions' in res else {}
        jur_state = self._get_jurisdiction_state(jurisdiction)
        county = jurisdiction['county'] if 'county' in jurisdiction else ''
        city = jurisdiction['city'] if 'city' in jurisdiction else ''
        # TODO: Add district IF it is shown by jurisdiction.

        for index, line in enumerate(self.order_line):
            if line.price_unit >= 0.0 and line.product_uom_qty >= 0.0:
                price = line.price_unit * \
                        (1 - (line.discount or 0.0) / 100.0) * \
                        line.product_uom_qty
                if price:
                    # Improve style, for + filter instead of 2 lines above
                    for item in items:
                        if item['id'] == str(line.id):
                            rates = self._prepare_breakdown_rates(item,
                                                                  jur_state,
                                                                  county,
                                                                  city)
                            taxes = []
                            for rate in rates:
                                tax = self.update_tax(rate,
                                                      taxable_account_id)
                                taxes.append(tax)
                            line.tax_id = [
                                (6, 0, [x.id for x in taxes])]
        return True
