# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _prepare_prq(self, installment):
        self.ensure_one()
        return {
            'type': 'purchase',
            'purchase_id': self.id,
            'installment': installment,
            'prepare_user_id': self.create_uid.id,
        }

    @api.multi
    def wkf_confirm_order(self):
        res = super(PurchaseOrder, self).wkf_confirm_order()
        Plan = self.env['purchase.invoice.plan']
        for order in self:
            if order.invoice_method != 'invoice_plan':
                continue
            installments = Plan.search([('order_id', '=', order.id)]) \
                .filtered(lambda l: l.require_prq is True) \
                .mapped('installment')
            for installment in list(set(installments)):
                ctx = {'installment': installment}
                prepare_prq = self._prepare_prq(installment)
                self.env['purchase.prq'].with_context(ctx).create(prepare_prq)
        return res

    @api.multi
    def action_invoice_create(self):
        """ Update prq when create invoice """
        res = super(PurchaseOrder, self).action_invoice_create()
        Plan = self.env['purchase.invoice.plan']
        for order in self:
            if order.invoice_method != 'invoice_plan':
                continue
            invoice_plan_prq = Plan.search([('order_id', '=', order.id)]) \
                .filtered(lambda l: l.require_prq is True)
            for plan in invoice_plan_prq:
                invoice = Plan.search(
                    [('order_id', '=', order.id),
                     ('installment', '=', plan.installment)])[0].ref_invoice_id
                prq = self.env['purchase.prq'].search([
                    ('purchase_id', '=', order.id),
                    ('installment', '=', plan.installment)
                ])
                prq.write({'invoice_id': invoice.id})
                prq.invoice_id.write({'prq_id': prq.id})
        return res
