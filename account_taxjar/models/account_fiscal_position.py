# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    is_nexus = fields.Boolean(string='Fiscal Position is a TaxJar Nexus')
    taxjar_id = fields.Many2one(
        'base.account.taxjar', string='TaxJar API ID')
    sourcing_type = fields.Selection([
        ('origin', 'Origin Sourcing'),
        ('destination', 'Destination Sourcing'),
    ])

    @api.multi
    def map_tax(self, taxes, product=None, partner=None):
        if self.is_nexus:
            return self.env['account.tax'].browse()
        else:
            return super(AccountFiscalPosition, self).map_tax(taxes,
                                                              product=product,
                                                              partner=partner)
