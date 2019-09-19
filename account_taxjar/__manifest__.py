# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Account TaxJar',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'summary': 'TaxJar SmartCalc API integration on Sale Invoices',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    "website": "https://www.eficent.com/",
    'depends': [
        'base_taxjar',
        'account',
        'sale_stock_sourcing_address',
    ],
    'data': [
        'data/account_tax_group.xml',
        'views/account_invoice_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
