# -*- coding: utf-8 -*-
from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context.copy()

        # Search Product Ref from Quotation Number
        if context.get('order_ref', False):
            custom_group = context.get('sale_order_line_ref_id', False)
            order = self.env['sale.order'].browse(context.get('order_ref'))
            product_ids = order.order_line.filtered(
                lambda r: r.sale_layout_custom_group == custom_group)
            args = [('id', 'in', product_ids.ids)] + args
        elif 'order_ref' in context:
            args = [('id', 'in', [])]

        # search Product Ref from sale order line
        if context.get('sale_order_line_ref_id', False):
            order_line = self.env['sale.order.line'].browse(
                context.get('sale_order_line_ref_id'))
            args = [('id', 'in', [order_line.product_id.id])] + args
        elif 'sale_order_line_ref_id' in context:
            args = [('id', 'in', [])]

        # Search products by category
        if context.get('po_type_id', False):
            po_type_id = context.get('po_type_id', [])
            PoTypeConfig = self.env['purchase.order.type.config']
            po_type_config = PoTypeConfig.browse(po_type_id)
            categ_ids = po_type_config.category_id.ids
            product = self.search([('categ_id', 'in', categ_ids)])
            args = [('id', 'in', product.ids)] + args
        elif 'po_type_id' in context:
            args = [('id', 'in', [])]

        return super(ProductProduct, self).name_search(
            name, args=args, operator=operator, limit=limit)
