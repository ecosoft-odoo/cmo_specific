# -*- coding: utf-8 -*-
from openerp import models, api, fields


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
    def _get_domain(self, domain):
        context = self._context.copy()
        # filter order line from quotation
        if context.get('order_ref', False):
            order = self.env['sale.order'].browse(context.get('order_ref'))
            domain = [('id', 'in', order.order_line.ids)] + domain
        elif 'order_ref' in context:
            domain = [('id', 'in', [])]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return super(SaleOrderLine, self).name_search(
            name, args=self._get_domain(args), operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,
                    limit=None, order=None):
        res = super(SaleOrderLine, self).search_read(
            domain=self._get_domain(domain), fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(SaleOrderLine, self).read_group(
            self._get_domain(domain), fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        return res

    @api.multi
    def name_get(self):
        if self._context.get('display_extended_name', False):
            result = []
            for rec in self:
                names = []
                if rec.sale_layout_custom_group:
                    names.append('%s' % rec.sale_layout_custom_group)
                if rec.sale_layout_cat_id:
                    names.append('%s' % rec.sale_layout_cat_id.name)
                if rec.name:
                    names.append(rec.name)
                result.append((rec.id, ' | '.join(names)))
        else:
            result = super(SaleOrderLine, self).name_get()
        return result


class SaleLayoutCategory(models.Model):
    _inherit = 'sale_layout.category'

    @api.model
    def _get_domain(self, domain):
        context = self._context.copy()
        # filter section from sale order line
        if context.get('sale_order_line_ref_id', False):
            order_line = self.env['sale.order.line'].browse(
                context.get('sale_order_line_ref_id'))
            domain = [('id', 'in', [order_line.sale_layout_cat_id.id])] + \
                domain
        elif 'sale_order_line_ref_id' in context:
            domain = [('id', 'in', [])]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return super(SaleLayoutCategory, self).name_search(
            name, args=self._get_domain(args),
            operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,
                    limit=None, order=None):
        res = super(SaleLayoutCategory, self).search_read(
            domain=self._get_domain(domain), fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(SaleOrderLine, self).read_group(
            self._get_domain(domain), fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        return res
