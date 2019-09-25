# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('base.account.taxjar', 'taxjar.api'),
    ('product.taxjar.category', 'taxjar.category'),
]

_table_renames = [
    (old.replace('.', '_'), new.replace('.', '_'))
    for (old, new) in _model_renames
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'base_account_taxjar') and \
            openupgrade.table_exists(cr, 'product_taxjar_category'):
        openupgrade.rename_models(cr, _model_renames)
        openupgrade.rename_tables(cr, _table_renames)
