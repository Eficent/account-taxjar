# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

from .taxjar_request import TaxJarRequest

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if invoice.fiscal_position_id.is_nexus and \
                    invoice.type in ['out_invoice', 'out_refund']:
                invoice.with_context(taxjar_authorize_transaction=True). \
                    prepare_taxes_on_invoice()
        return super(AccountInvoice, self).action_invoice_open()

    @staticmethod
    def _get_rate(request, lines, partner, company, nexus):
        try:
            res = request.get_rate(lines, partner, company, nexus)
        except Exception as e:
            raise ValidationError(_("TaxJar SmartCalc API Error: "+str(e)))
        return res

    def _get_nexus(self):
        return self.fiscal_position_id

    def _get_partner(self):
        return self.partner_id

    def _get_lines(self):
        lines = []
        for line in self.invoice_line_ids:
            lines.append(line)
        return lines
    
    def _get_jur_state(self, jurisdiction):
        state_id = self.env['res.country.state'].search([
            ('code', '=', jurisdiction['state']),
            ('country_id.code', '=', jurisdiction['country'])
        ])
        return state_id
    
    @staticmethod
    def _prepare_breakdown_rates(item, jur_state, county, city):
        # TODO: As we find amount = 0 here maybe it is interesting to
        #  remove logic from main loop, more Pythonic,
        precision = 3
        state_tax_amount = float_round(item['state_sales_tax_rate'] * 100,
                                       precision_digits=precision)
        county_tax_amount = float_round(item['county_tax_rate'] * 100,
                                        precision_digits=precision)
        city_tax_amount = float_round(item['city_tax_rate'] * 100,
                                      precision_digits=precision)
        special_tax_amount = float_round(item['special_tax_rate'] * 100,
                                         precision_digits=precision)
        res = [
            {
                'name': 'State Tax: %s: %.3f %%' % (
                    jur_state.code, state_tax_amount),
                'amount': state_tax_amount,
                'state_id': jur_state.id
            },
            {
                'name': 'County Tax: %s/%s %.3f %%' % (
                    jur_state.code, county, county_tax_amount),
                'amount': county_tax_amount,
                'county': county,
                'state_id': jur_state.id
            },
            {
                'name': 'City Tax: %s/%s/%s %.3f %%' % (
                    city, county, jur_state.code, city_tax_amount),
                'amount': city_tax_amount,
                'city': city,
                'county': county,
                'state_id': jur_state.id

            },
            {
                'name': 'Special District Tax: %s/%s/%s %.3f %%' % (
                    city, county, jur_state.code, special_tax_amount),
                'amount': special_tax_amount,
                'city': city,
                'county': county,
                'state_id': jur_state.id
            },
        ]
        return res
    
    def update_tax(self, tax, jur_state, taxable_account_id):
        city = tax['city'] if 'city' in tax else ''
        county = tax['county'] if 'county' in tax else ''
        state_id = tax['state_id']
        account_tax = self.env['account.tax']
        amount = tax['amount']
        name = tax['name']
        # TODO: As account.tax have constraint unique for name maybe
        #       it is only need to look for name, will increase performance?
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
                'state_id': jur_state.id,
                'city': city,
                'county': county,
            }
            tax = account_tax.sudo().create(tax_dict)
        return tax

    @api.multi
    def prepare_taxes_on_invoice(self):
        company = self.company_id or self.env.user.company_id
        partner = self._get_partner()
        nexus = self._get_nexus()
        lines = self._get_lines()
        if not company or not partner or not nexus or not lines:
            raise ValidationError(_("Request cannot be executed due to: "
                                    "company, partner, nexus or invoice lines"
                                    "don't exist"))
        taxable_account_id = \
            self.fiscal_position_id.taxjar_id.sudo().taxable_account_id.id
        api_url = self.fiscal_position_id.taxjar_id.sudo().taxjar_api_url
        api_token = self.fiscal_position_id.taxjar_id.sudo().taxjar_api_token
        request = TaxJarRequest(api_url, api_token)

        res = self._get_rate(request, lines, partner, company, nexus)

        items = res['breakdown']['line_items'] if 'breakdown' in res else {}
        jurisdiction = res['jurisdictions'] if 'jurisdictions' in res else {}
        jur_state = self._get_jur_state(jurisdiction)
        county = jurisdiction['county'] if 'county' in jurisdiction else ''
        city = jurisdiction['city'] if 'city' in jurisdiction else ''
        # TODO: Add district IF it is shown by jurisdiction.
        #       it has never been shown in requests before.
        for index, line in enumerate(self.invoice_line_ids):
            if line.price_unit >= 0.0 and line.quantity >= 0.0:
                price = line.price_unit * \
                        (1 - (line.discount or 0.0) / 100.0) * \
                        line.uom_id._compute_quantity(
                            line.quantity, line.product_id.uom_id, round=False)
                if price:
                    for item in items:
                        # TODO: Test failing because on test fixture
                        #       invoice_line_id is not syncronized with
                        #       cassettes
                        if item['id'] == str(line.id):
                            rates = self._prepare_breakdown_rates(item,
                                                                  jur_state,
                                                                  county,
                                                                  city)
                            taxes = []
                            for rate in rates:
                                tax = self.update_tax(rate,
                                                      jur_state,
                                                      taxable_account_id)
                                taxes.append(tax)
                            line.invoice_line_tax_ids = [
                                (6, 0, [x.id for x in taxes])]
        self._onchange_invoice_line_ids()
        return True
