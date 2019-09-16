# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    state_id = fields.Many2one('res.country.state')
    county = fields.Char()
    city = fields.Char()
