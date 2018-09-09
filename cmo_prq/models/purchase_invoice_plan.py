# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseInvoicePlan(models.Model):
    _inherit = 'purchase.invoice.plan'

    require_prq = fields.Boolean(
        string='PRQ',
        default=False,
        help='Can not create invoice until PRQ is approve',
    )

    @api.onchange('require_prq')
    def _onchange_require_prq(self):
        Plan = self.env['purchase.invoice.plan']
        dom = [('order_id', '=', self._origin.order_id.id),
               ('installment', '=', self._origin.installment)]
        plan = Plan.search(dom)
        plan.write({'require_prq': self.require_prq})
