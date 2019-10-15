# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

__name__ = "Post-Migration account_taxjar to 12.0.1.0.0"

_model_renames = [
    ('base.account.taxjar', 'taxjar.api.key'),
    ('product.taxjar.category', 'taxjar.category'),
]

_table_renames = [
    (old.replace('.', '_'), new.replace('.', '_'))
    for (old, new) in _model_renames
]


def _int_to_str_taxjar_category_code(env):
    _logger.info("Changing column type from int to str for "
                 "product_taxjar_category table on code column")
    env.cr.execute("""
        ALTER TABLE product_taxjar_category
        ALTER COLUMN code TYPE VARCHAR USING code::varchar;
        """)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    _int_to_str_taxjar_category_code(env)
    if openupgrade.table_exists(cr, 'base_account_taxjar') and \
            openupgrade.table_exists(cr, 'product_taxjar_category'):
        openupgrade.rename_models(cr, _model_renames)
        openupgrade.rename_tables(cr, _table_renames)
