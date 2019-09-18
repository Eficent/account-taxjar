# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Base TaxJar',
    'version': '12.0.1.0.0',
    'category': 'Account',
    'summary': 'TaxJar SmartCalc API integration',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    "website": "https://www.eficent.com/",
    'depends': [
        'base',
    ],
    'external_dependencies': {'python': ['taxjar']},
    'data': [
        'security/ir.model.access.csv',
        'views/taxjar_api_views.xml',
        'views/taxjar_nexus_sourcing_views.xml',
        'views/taxjar_category_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
