# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

__name__ = "Post-Migration account_taxjar to 12.0.1.0.0"


def _migrate_account_fiscal_position_to_taxjar_nexus_sourcing(env):
    _logger.info("Migrating nexus paramenters from account_fiscal_position to"
                 " taxjar_nexus_sourcing")
    env.cr.execute("""
    SELECT afp.id, afp.name, afp.taxjar_id, afp.sourcing_type,
           tak.taxable_account_id
    FROM account_fiscal_position AS afp
    INNER JOIN taxjar_api_key AS tak ON tak.id = afp.taxjar_id
    WHERE afp.is_nexus = TRUE;
    """)
    taxjar_nexus_sourcing = env['taxjar.nexus.sourcing']
    account_fiscal_position = env['account.fiscal.position']
    for afp_id, name, taxjar_id, sourcing_type, taxable_account_id\
            in env.cr.fetchall():
        tns = taxjar_nexus_sourcing.create({
            'name': name,
            'taxjar_id': taxjar_id,
            'sourcing_type': sourcing_type,
            'taxable_account_id': taxable_account_id,
        })
        afp = account_fiscal_position.browse(afp_id)
        afp.write({'taxjar_nexus_sourcing_id': tns.id})


@openupgrade.migrate()
def migrate(env, version):
    _migrate_account_fiscal_position_to_taxjar_nexus_sourcing(env)
