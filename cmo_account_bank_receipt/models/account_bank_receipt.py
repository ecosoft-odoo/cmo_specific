# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approver',
        copy=False,
        track_visibility='onchange',
    )
    approver_job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Approver Position',
        copy=False,
        track_visibility='onchange',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountBankReceipt, self).default_get(fields)
        approver = self.env.user.company_id.approver_id
        res.update({
            'approver_id': approver.id,
            'approver_job_id': approver.job_id.id
        })
        return res
