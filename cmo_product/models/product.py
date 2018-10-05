# -*- coding: utf-8 -*-
from openerp import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'id'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Product Name must be unique')
    ]


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'id'
