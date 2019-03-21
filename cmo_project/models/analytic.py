# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    expense_related_ids = fields.One2many(
        'hr.expense.line',
        'analytic_account',
        string='Related Expense',
    )

    @api.model
    def create(self, vals):
        if self._context.get('alias_parent_model_name') == 'project.project':
            ctx = {'fiscalyear_id': self.env['account.fiscalyear'].find()}
            vals['code'] = \
                self.env['ir.sequence'].with_context(ctx).get('cmo.project')
        res = super(AccountAnalyticAccount, self).create(vals)
        return res
