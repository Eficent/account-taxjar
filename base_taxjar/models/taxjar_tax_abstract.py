# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round
from odoo.addons.bus.models.bus import json_dump

from .taxjar_request import TaxJarRequest

_logger = logging.getLogger(__name__)


class TaxJarTaxAbstract(models.AbstractModel):
    _name = 'taxjar.tax.abstract'
    _description = 'TaxJar API Tax Generator'

    show_taxjar_button = fields.Boolean(
        'Hide TaxJar Button',
        compute='_compute_hide_taxjar_button', default=False)

    @api.depends('fiscal_position_id', 'state')
    def _compute_hide_taxjar_button(self):
        for rec in self:
            if rec.state == 'draft' and rec.fiscal_position_id.taxjar_id:
                rec.show_taxjar_button = True

    @staticmethod
    def _get_rate(request, lines, from_address, to_address):
        try:
            res = request.get_rate(lines, from_address, to_address)
        except Exception as e:
            raise ValidationError(_("TaxJar SmartCalc API Error: "+str(e)))
        return res

    def _get_from_addresses(self):
        """
            :return: partner_id of origin's address.
        """
        raise NotImplementedError()

    def _get_to_address(self):
        """
            :return: partner_id of origin's address.
        """
        raise NotImplementedError()

    def _get_lines_from_address(self, from_address):
        lines = []
        for line in self.invoice_line_ids.filtered(
                lambda l: l.warehouse_id.partner_id == from_address):
            lines.append(line)
        return lines

    def _get_jur_state(self, jurisdiction):
        state_id = self.env['res.country.state'].search([
            ('code', '=', jurisdiction['state']),
            ('country_id.code', '=', jurisdiction['country'])
        ])
        return state_id

    @staticmethod
    def _get_price(line):
        """
            :return: partner_id of origin's address.
        """
        raise NotImplementedError()

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
                  ]

        tax = account_tax.sudo().search(domain, limit=1)
        if not tax:
            tax_dict = {
                'name': name,
                'amount': amount,
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'description': name,
                'account_id': taxable_account_id,
                'refund_account_id': taxable_account_id,
                'state_id': state_id,
                'city': city,
                'county': county,
                'tax_group_id': self.env.ref(tax_group).id
            }
            tax = account_tax.sudo().create(tax_dict)
        return tax

    @staticmethod
    def _set_tax_ids(line, taxes):
        """ Set taxes ids for specific models. """
        raise NotImplementedError()

    @api.multi
    def prepare_taxes(self):
        to_address = self._get_to_address()
        from_addresses = self._get_from_addresses()

        if not from_addresses or not to_address:
            raise ValidationError(_("Request cannot be executed due to: "
                                    "company, partner, nexus"
                                    "don't exist"))
        taxable_account_id = \
            self.fiscal_position_id.taxjar_id.sudo().taxable_account_id.id
        api_url = self.fiscal_position_id.taxjar_id.sudo().taxjar_api_url
        api_token = self.fiscal_position_id.taxjar_id.sudo().taxjar_api_token
        request = TaxJarRequest(api_url, api_token)

        for from_address in from_addresses:
            lines = self._get_lines_from_address(from_address)
            if not lines:
                raise ValidationError(_("Invoice lines not found!"))
            res = self._get_rate(request, lines, to_address, from_address)
            items = res['breakdown']['line_items'] \
                if 'breakdown' in res else {}
            jurisdiction = res['jurisdictions'] \
                if 'jurisdictions' in res else False
            if not jurisdiction['state']:
                # We need to ensure how workflow works. What happens if there
                # is no tax related, so TaxJar don't return a proper response.
                # TODO: ~ Check requeriments ~
                # * Address of the customer is noy set correctly for USA
                # * Products are sold outside USA (TaxJar required?)
                # * Alternative Warehouse Locations (don't use company address)
                raise ValidationError(_("TaxJar did not found "
                                        "a Jurisdiction for in:\n%s\n"
                                        "Review Fiscal Position. (DEV)"
                                        % json_dump(res['jurisdictions'])))

            jur_state = self._get_jur_state(jurisdiction)
            county = jurisdiction['county'] if 'county' in jurisdiction else ''
            city = jurisdiction['city'] if 'city' in jurisdiction else ''
            # TODO: Add district IF it is shown by jurisdiction.
            #       it has never been shown in requests before.
            for line in lines:
                price_unit, quantity, discount = self._get_price(line)
                if price_unit >= 0.0 and quantity >= 0.0:
                    price = price_unit * \
                        (1 - (discount or 0.0) / 100.0) * quantity
                    if price:
                        for item in items:
                            if item['id'] == str(line.id):
                                rates = self._prepare_breakdown_rates(
                                    item,
                                    jur_state,
                                    county,
                                    city)
                                taxes = []
                                for rate in rates:
                                    tax = self.update_tax(rate,
                                                          taxable_account_id)
                                    taxes.append(tax)
                                self._set_tax_ids(line, taxes)
                                break
        self.with_context(mail_notrack=True).message_post(
            body=_('Successfully updated Taxes from TaxJar'))
        return True
