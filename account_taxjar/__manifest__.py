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
    ],
    'data': [
        'views/account_invoice_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
