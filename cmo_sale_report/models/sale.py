# -*- coding: utf-8 -*-
from openerp import models, api


def filter_print_report(res, reports):
    action = []
    if res.get('toolbar', {}) and res.get('toolbar').get('print', False):
        for act in res.get('toolbar').get('print'):
            if act.get('report_name') in reports:
                continue
            action.append(act)
        res['toolbar']['print'] = action
    return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        context = self._context.copy()
        if context.get('order_type', False) == 'quotation':
            # Report name for remove out from print button
            reports = [
                u'cmo.sale.order',
                u'cmo.sale.order.th',
                u'cmo.sale.order.est',
                u'cmo.sale.order.add',
            ]
            filter_print_report(res, reports)
        return res
