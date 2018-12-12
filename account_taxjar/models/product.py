
from odoo import api, fields, models, _


class ProductTaxCode(models.Model):
    _name = 'product.tax.code'
    _description = "Taxjar Product Tax Code"
    _rec_name = 'code'

    code = fields.Integer(string="Product Tax Code", required=True)
    description = fields.Char(string="Product Tax Description", required=True)
    name = fields.Char(string="Product Tax Name", required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            tax_code_ids = self.search([('description', operator, name)] + args,
                                       limit=limit,
                                       acces_rights_uid=name_get_uid)
        if not tax_code_ids:
            tax_code_ids = self._search([('code', operator, name)] + args,
                                        limit=limit,
                                        access_rights_uid=name_get_uid)
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

    tax_code_id = fields.Many2one('product.tax.code',
                                  string="Taxjar Product Tax Code")


# TODO: To delete, Does it make sense to have default tax for company
class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_code_id = fields.Many2one('product.tax.code',
                                  string="Taxjar Product Tax Code")


class ProductCategory(models.Model):
    _inherit = 'product.category'

    tax_code_id = fields.Many2one('product.tax.code',
                                  string="Taxjar Product Tax Code")
