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


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'taxjar.tax.abstract']

    show_taxjar_button = fields.Boolean(
        'Hide TaxJar Button',
        compute='_compute_hide_taxjar_button', default=False)

    # If we have several warehouses on account_invoice_lines we need to get
    # their related partner.
    def _get_from_addresses(self):
        return list(
            set(self.invoice_line_ids.mapped('warehouse_id.partner_id')))

    def _get_to_address(self):
        return self.partner_id

    def _get_lines(self, from_address):
        lines = []
        for line in self.invoice_line_ids.filtered(
                lambda l: l.warehouse_id.partner_id == from_address):
            lines.append(line)
        return lines

    def prepare_taxes(self):
        super().prepare_taxes()
        # Force on change to update taxes on view.
        self._onchange_invoice_line_ids()
        return True
