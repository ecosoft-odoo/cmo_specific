# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _prepare_prq(self, installment, invoice):
        self.ensure_one()
        return {
            'type': 'purchase',
            'purchase_id': self.id,
            'invoice_id': invoice.id,
            'installment': installment,
            'prepare_user_id': self.create_uid.id,
        }

    @api.multi
    def action_invoice_create(self):
        res = super(PurchaseOrder, self).action_invoice_create()
        Plan = self.env['purchase.invoice.plan']
        for order in self:
            if order.invoice_method != 'invoice_plan':
                continue
            installments = Plan.search([('order_id', '=', order.id)]) \
                .filtered(lambda l: l.require_prq is True) \
                .mapped('installment')
            for installment in list(set(installments)):
                invoice = Plan.search(
                    [('order_id', '=', order.id),
                     ('installment', '=', installment)])[0].ref_invoice_id
                prepare_prq = self._prepare_prq(installment, invoice)
                prq = self.env['purchase.prq'].create(prepare_prq)
                prq.invoice_id.write({'prq_id': prq.id})
        return res
