# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpenseCancel(models.TransientModel):
    _inherit = 'hr.expense.cancel'

    @api.model
    def view_init(self, fields_list):
        expense_id = self._context.get('active_id')
        expense = self.env['hr.expense.expense'].browse(expense_id)
        expense._check_extra_permission(type="refuse")
