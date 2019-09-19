# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class TaxJarBreakdownTax(models.Model):
    _name = 'taxjar.breakdown.tax'
    _description = 'Add address info of tax collections'

    state_id = fields.Many2one('res.country.state')
    county = fields.Char()
    city = fields.Char()

    @staticmethod
    def _get_update_tax_domain(tax):
        """ Get update tax domain. """
        raise NotImplementedError()

    def _create_taxjar_tax(self, tax, taxable_account_id):
        """ Create tax domain. """
        raise NotImplementedError()
