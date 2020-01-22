# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

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
