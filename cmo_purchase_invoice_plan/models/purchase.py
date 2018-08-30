# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    prq_ids = fields.One2many(
        'purchase.prq',
        'purchase_id',
        string='Invoice Plan',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def _prepare_prq_vals(self, order, name, plan):
        prq_vals = {
            'name': name,
            'ref': order.name,
            'installment': plan.installment,
            'purchase_id': order.id,
            'prepare_user_id': order.approve_id.id,
            'approve_user_id': order.approver_ids.id,
        }
        return prq_vals

    @api.multi
    def action_invoice_create(self):
        res = super(PurchaseOrder, self).action_invoice_create()
        self.action_prq_create()
        return res

    @api.multi
    def action_prq_create(self):
        Prq = self.env['purchase.prq']
        for order in self:
            if order.invoice_plan_ids:
                for plan in order.invoice_plan_ids:
                    if plan.require_prq:
                        refer_type = 'purchase'
                        doctype = order.env['res.doctype'].get_doctype(refer_type)
                        fiscalyear_id = order.env['account.fiscalyear'].find()
                        order = order.with_context(doctype_id=doctype.id,
                                                    fiscalyear_id=fiscalyear_id)
                        name = order.env['ir.sequence'].next_by_code(
                            'purchase.prq')

                        prq_vals = self._prepare_prq_vals(order, name, plan)
                        Prq.create(prq_vals)
