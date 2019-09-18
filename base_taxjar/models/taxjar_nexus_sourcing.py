# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class TaxJarNexusSourcing(models.Model):
    _name = 'taxjar.nexus.sourcing'
    _description = 'TaxJar Nexus Sourcing'
    _rec_name = 'name'

    name = fields.Char('Name')
    taxjar_id = fields.Many2one('taxjar.api', string='TaxJar API ID')
    sourcing_type = fields.Selection([
        ('origin', 'Origin Sourcing'),
        ('destination', 'Destination Sourcing'),
    ])
