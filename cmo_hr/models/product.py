# -*- coding: utf-8 -*-
from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_domain(self, domain):
        context = self._context.copy()
        # Search products by category
        if context.get('pay_to', False) == 'pettycash':
            product_ids = self.env['product.product']
            product = product_ids.search([('categ_id.hr_product', '=', False)])
            domain += [('id', 'in', product.ids)]
        return domain
