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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self._context.get('company_id', self.env.user.company_id)
    )
    account_report_approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Accounting Report Approver',
        default=lambda self: self.env.user.company_id.account_report_approver_id,
    )
    account_report_approver_job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Accounting Report Approver Position',
        default=lambda self: self.env.user.company_id.account_report_approver_id.job_id,
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
