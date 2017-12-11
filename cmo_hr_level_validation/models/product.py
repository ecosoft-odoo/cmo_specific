# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    hr_product = fields.Boolean(
        string='HR Product',
        default=False,
    )
