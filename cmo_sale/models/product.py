# -*- coding: utf-8 -*-

from openerp import fields, models, api


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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        if len(vals) == 1 and 'product_tmpl_id' in vals:
            self = self.sudo()
        return super(ProductProduct, self).write(vals)
