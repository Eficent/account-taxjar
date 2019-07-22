# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ProductTaxJarCategory(models.Model):
    _name = 'product.taxjar.category'
    _description = "TaxJar Product Tax Code"
    _rec_name = 'code'

    code = fields.Integer(string="Product Tax Code", required=True)
    description = fields.Char(string="Product Tax Description", required=True)
    name = fields.Char(string="Product Tax Name", required=True)

    taxjar_id = fields.Many2one(
        'base.account.taxjar', 'TaxJar API ID',
        required=True, ondelete='cascade'
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        args = args or []
        tax_code_ids = []
        access_rights_uid = name_get_uid or self._uid
        if name:
            tax_code_ids = self.search(
                [('description', operator, name)] + args, limit=limit,
                access_rights_uid=access_rights_uid)
        if not tax_code_ids:
            tax_code_ids = self._search([('code', operator, name)] + args,
                                        limit=limit,
                                        access_rights_uid=access_rights_uid)
        return self.browse(tax_code_ids).name_get()

    @api.multi
    def name_get(self):
        res = []
        for category in self:
            res.append((category.id,
                        _('[%s] %s') % (category.code, category.description)))
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tax_code_id = fields.Many2one('product.taxjar.category',
                                  string="TaxJar Product Tax Code")


class ProductCategory(models.Model):
    _inherit = 'product.category'

    tax_code_id = fields.Many2one('product.taxjar.category',
                                  string="TaxJar Product Tax Code")
