# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_layout_cat_id = fields.Many2one(
        'sale_layout.category',
        string='Section',
    )
    management_fee = fields.Boolean(
        related='sale_layout_cat_id.management_fee',
        string='Management Fee',
        default=False,
    )
