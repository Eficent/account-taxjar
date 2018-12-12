
import logging
import re

_logger = logging.getLogger(__name__)

try:
    import taxjar
except ImportError:
    _logger.debug("`taxjar` Python library not installed.")

from odoo import modules
from odoo.exceptions import ValidationError


class TaxjarRequest(object):

    def __init__(self, api_url, api_key):
        self.taxjar = taxjar.Client(api_key, api_url)

    def get_product_tax_code(self):
        try:
            res = self.taxjar.categories()
            print(res)
        except Exception as e:
            raise ValidationError(
                'Unable to communicate with Taxjar API: ' + '\n' + str(e))
            pass
        return res

    def get_nexus_regions(self):
        try:
            res = self.taxjar.nexus_regions()
            print(res)
        except Exception as e:
            raise ValidationError(
                'Unable to communicate with Taxjar API: ' + '\n' + str(e))
            pass
        return res





