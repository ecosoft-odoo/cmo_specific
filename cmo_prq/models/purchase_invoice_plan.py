# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseInvoicePlan(models.Model):
    _inherit = 'purchase.invoice.plan'

    is_prq = fields.Boolean(
        string='PRQ',
        default=False,
    )

    @api.onchange('is_prq')
    def _onchange_is_prq(self):
        Plan = self.env['purchase.invoice.plan']
        dom = [('order_id', '=', self._origin.order_id.id),
               ('installment', '=', self._origin.installment)]
        plan = Plan.search(dom)
        plan.write({'is_prq': self.is_prq})
