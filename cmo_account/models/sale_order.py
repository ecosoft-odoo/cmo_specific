# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _make_invoice(self, order, lines):
        res = super(SaleOrder, self)._make_invoice(order, lines)
        inv = self.env['account.invoice'].browse(res)
        if order:
            quote_id = order.quote_id or False
            if quote_id:
                inv.write({
                    'quote_ref_id': quote_id.id,
                    'quote_ref_date': quote_id.date_order.split(' ')[0],
                })
                project_id = quote_id.project_related_id or False
                if project_id:
                    inv.write({
                        'project_ref_id': project_id.id,
                    })
        return res
