# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SupplierBilling(models.Model):
    _inherit = 'supplier.billing'

    billing_active = fields.Boolean(
        compute='_compute_billing_active',
        string='Billing Active in Payment',
        store=True,
        help='Bill active in supplier payment when state invoice equal '
             'open or cancel (do not appear other state)',
    )

    @api.multi
    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_billing_active(self):
        for billing in self:
            invoice_states = billing.invoice_ids.mapped('state')
            billing.billing_active = True
            if list(filter(lambda x: x not in ['open', 'cancel'],
                           invoice_states)):
                billing.billing_active = False

    
