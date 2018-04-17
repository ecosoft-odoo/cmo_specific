# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class EditAnalyticAccount(models.TransientModel):
    _name = 'edit.analytic.account'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditAnalyticAccount, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        if not rec.expense_id.state == 'validate':
            raise ValidationError(
                _('Only in state "Waiting Validate", amount can be edited'))
        res['analytic_account_id'] = rec.analytic_account.id
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        rec.write({'analytic_account': rec.analytic_account.id})
        return True
