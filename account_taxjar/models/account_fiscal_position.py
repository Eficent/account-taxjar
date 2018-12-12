
from odoo import api, fields, models, _


class AccountFiscalPositionTemplate(models.Model):
    _inherit = 'account.fiscal.position.template'

    is_taxjar = fields.Boolean(string='Use Taxjar API')


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    is_taxjar = fields.Boolean(string='Use Taxjar API')

    @api.multi
    def map_tax(self, taxes, product=None, partner=None):


        if self.is_taxjar:
            return self.env['account.tax'].browse()
        else:
            return super(AccountFiscalPosition, self).map_tax(taxes,
                                                              product=product,
                                                              partner=partner)


class AccountFiscalPositionTaxTemplate(models.Model):
    _inherit = 'account.fiscal.position.tax.template'

    tax_code_ids = fields.Many2many('product.tax.code',
                                    string="Product tax code")
    state_ids = fields.Many2many('res.country.state', string="Federal States")
    zip_codes = fields.Char(string="Zip")


class AccountFiscalPositionTax(models.Model):
    _inherit = 'account.fiscal.position.tax'

    tax_code_ids = fields.Many2many('product.tax.code',
                                    string="Product tax code")
    state_ids = fields.Many2many('res.country.state', string="Federal States")
    zip_codes = fields.Char(string="Zip")

