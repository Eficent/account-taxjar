# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account TaxJar',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'summary': 'TaxJar SmartCalc API integration on Sale Invoices',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    "website": "https://www.eficent.com/",
    'depends': [
        'l10n_us',
        'account_invoicing',
        'sale_order_line_sourcing_address'
    ],
    'external_dependencies': {'python': ['taxjar']},
    'data': [
        'security/ir.model.access.csv',
        'data/account_tax_group.xml',
        'views/base_account_taxjar_views.xml',
        'views/account_fiscal_position_views.xml',
        'views/account_invoice_views.xml',
        'views/product_taxjar_category_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
