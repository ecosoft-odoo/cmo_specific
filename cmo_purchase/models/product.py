# -*- coding: utf-8 -*-
from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_domain(self, domain):
        context = self._context.copy()

        # Search Product Ref from Quotation Number
        if context.get('order_ref', False):
            custom_group = context.get('sale_order_line_ref_id', False)
            order = self.env['sale.order'].browse(context.get('order_ref'))
            product_ids = order.order_line.filtered(
                lambda r: r.sale_layout_custom_group == custom_group)
            domain += [('id', 'in', product_ids.ids)]
        elif 'order_ref' in context:
            domain += [('id', 'in', [])]

        # search Product Ref from sale order line
        if context.get('sale_order_line_ref_id', False):
            order_line = self.env['sale.order.line'].browse(
                context.get('sale_order_line_ref_id'))
            domain += [('id', 'in', [order_line.product_id.id])]
        elif 'sale_order_line_ref_id' in context:
            domain += [('id', 'in', [])]

        # Search products by category
        if context.get('po_type_id', False):
            po_type_id = context.get('po_type_id', [])
            PoTypeConfig = self.env['purchase.order.type.config']
            po_type_config = PoTypeConfig.browse(po_type_id)
            categ_ids = po_type_config.category_ids.ids
            product = self.search([('categ_id', 'in', categ_ids)])
            domain += [('id', 'in', product.ids)]
        elif 'po_type_id' in context:
            domain += [('id', 'in', [])]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return super(ProductProduct, self).name_search(
            name, args=self._get_domain(args), operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,
                    limit=None, order=None):
        res = super(ProductProduct, self).search_read(
            domain=self._get_domain(domain), fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(ProductProduct, self).read_group(
            self._get_domain(domain), fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        return res
