# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    # TODO: Is it this necessary? Why?
    def _get_partner(self):
        return self.partner_shipping_id or \
               super(AccountInvoice, self)._get_partner()
