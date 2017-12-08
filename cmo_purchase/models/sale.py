# -*- coding: utf-8 -*-
from openerp import models, api


# class SaleLayoutCustomGroup(models.Model):
#     _inherit = 'sale_layout.custom_group'
#
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         context = self._context.copy()
#         if context.get('order_ref', False):
#             order = self.env['sale.order'].browse(context.get('order_ref'))
#             group_ids = order.order_line.mapped(
#                 'sale_layout_custom_group_id.id')
#             args = [('id', 'in', group_ids)] + args
#         elif 'order_ref' in context:
#             args = [('id', 'in', [])]
#         return super(SaleLayoutCustomGroup, self).name_search(
#             name, args=args, operator=operator, limit=limit)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context.copy()
        # filter order line from quotation
        if context.get('order_ref', False):
            order = self.env['sale.order'].browse(context.get('order_ref'))
            args = [('id', 'in', order.order_line.ids)] + args
        elif 'order_ref' in context:
            args = [('id', 'in', [])]

        return super(SaleOrderLine, self).name_search(
            name, args=args, operator=operator, limit=limit)


class SaleLayoutCategory(models.Model):
    _inherit = 'sale_layout.category'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context.copy()
        # filter section from sale order line
        if context.get('sale_order_line_ref_id', False):
            order_line = self.env['sale.order.line'].browse(
                context.get('sale_order_line_ref_id'))
            args = [('id', 'in', [order_line.sale_layout_cat_id.id])] + args
        elif 'sale_order_line_ref_id' in context:
            args = [('id', 'in', [])]
        return super(SaleLayoutCategory, self).name_search(
            name, args=args, operator=operator, limit=limit)
