# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class TaxJarNexusSourcing(models.Model):
    _inherit = 'taxjar.nexus.sourcing'

    taxable_account_id = fields.Many2one(
        'account.account', string='Taxable Account TaxJar',
    )
