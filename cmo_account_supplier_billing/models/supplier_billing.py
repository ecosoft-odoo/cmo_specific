# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SupplierBilling(models.Model):
    _name = 'supplier.billing'
    _inherit = ['supplier.billing', 'mail.thread']

    billing_active = fields.Boolean(
        compute='_compute_billing_active',
        string='Billing Active in Payment',
        store=True,
        help='Bill active in supplier payment when state invoice equal '
             'open or cancel (do not appear other state)',
    )

    current_user = fields.Char(
        compute='_get_current_user',
    )

    @api.multi
    def action_billed(self):
        self.ensure_one()
        self.message_post("This document has been billed")
        return super(SupplierBilling,self).action_billed()

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.message_post("This document has been cancelled")
        return super(SupplierBilling,self).action_cancel()


    @api.one
    def _get_current_user(self):
        self.current_user = self.env.user.name
        return

    @api.multi
    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_billing_active(self):
        for billing in self:
            invoice_states = billing.invoice_ids.mapped('state')
            billing.billing_active = True
            if list(filter(lambda x: x not in ['open', 'cancel'],
                           invoice_states)):
                billing.billing_active = False
