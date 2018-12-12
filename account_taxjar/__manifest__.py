# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Taxjar',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'summary': 'Taxjar taxaction',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    "website": "https://www.eficent.com/",
    'depends': [
        'l10n_us',
    ],
    'external_dependencies': {'python': ['taxjar']},
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position_view.xml',
        'views/account_invoice_views.xml',
        'views/product_view.xml',
        'views/res_config_settings_views.xml',
        'data/account_taxjar_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}