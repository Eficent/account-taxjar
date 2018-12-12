
import datetime
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round

from .taxjar_request import TaxjarRequest

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if invoice.fiscal_position_id.is_taxjar and invoice.type in [
                'out_invoice', 'out_refund']:
                invoice.with_context(taxjar_authorize_transaction=True).validate_taxes_on_invoice()
        return super(AccountInvoice, self).action_invoice_open()

    def _get_partner(self):
        return self.partner_id

    @api.multi
    def validate_taxes_on_invoice(self):
        config_parameter = self.env['ir.config_parameter']
        api_url = config_parameter.get_param('account_taxjar.taxjar_api_url')
        api_key = config_parameter.get_param('account_taxjar.taxjar_api_key')
        request = TaxjarRequest(api_url, api_key)

        shipper = self.company_id or self.env.user.company_id
        request.set_location_origin_detail(shipper)
        request.set_location_destination_detail(self._get_partner())

        request.set_invoice_items_detail(self)

        response = request.get_all_taxes_values()

        if response.get('error_message'):
            raise ValidationError(
                _('Unable to retrieve taxes from Taxjar: ') + '\n' + response[
                    'error_message'])

        tax_values = response['values']

        # TODO: Finish

    @api.multi
    def action_invoice_paid(self):
        for invoice in self:
            if invoice.fiscal_position_id.is_taxjar:
                config_parameter = self.env['ir.config_parameter']
                api_url = config_parameter.get_param(
                    'account_taxjar.taxjar_api_url')
                api_key = config_parameter.get_param(
                    'account_taxjar.taxjar_api_key')
                request = TaxjarRequest(api_url, api_key)
                if invoice.type == 'out_invoice':
                    pass
                    # request.transaction()
                    # TODO: Finish
                else:
                    request.set_invoice_items_detail(invoice)
                    origin_invoice = self.env['account.invoice'].search(
                        [('number', '=', invoice.origin)], limit=1)
                    if origin_invoice:
                        pass
                        #request.return
                    else:
                        _logger.warning(_("The source document on the refund is not valid and thus the refunded cart won't be logged on your taxcloud account"))

        return super(AccountInvoice, self). action_invoice_paid()



