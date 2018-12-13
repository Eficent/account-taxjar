# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    state_id = fields.Many2one('res.country.state')
    county = fields.Char()
    city = fields.Char()
