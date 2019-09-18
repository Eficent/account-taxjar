Base module for `TaxJar SmartCalcs API <https://www.taxjar.com/smartcalcs/>`_.

It requires from module `account_taxjar` to add tax calculation to invoice
It requires from module `sale_account_taxjar` to add tax calculation to sale orders

This module does:

 * Import/update TaxJar product categories.
 * Import/update TaxJar Nexus.
 * Request for a Tax Rate calculation.

This module does't:

 * Manage transactions with TaxJar Dashboard
 * Manage customers with TaxJar Dashboard
 * Validate addresses
