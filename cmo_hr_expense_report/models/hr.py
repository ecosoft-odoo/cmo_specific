# -*- coding: utf-8 -*-

from openerp import fields, models, api


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
            toolbar=False,submenu=False):
        res = super(HrExpenseExpense, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # HR Expense
        if self._context.get('is_advance_clearing', False) is False and\
                self._context.get('is_employee_advance', False) is False and\
                self._context.get('default_is_advance_clearing', False) is False:
            reports = [
                u'HR/Expense',
            ]
            self.filter_print_report(res, reports)
        # HR Advance
        elif self._context.get('default_is_employee_advance', False) and\
                self._context.get('is_employee_advance', False):
            reports = [
                u'HR/Advance',
            ]
            self.filter_print_report(res, reports)
        # HR Advance Clearing
        elif self._context.get('default_is_employee_advance', False) is False \
                and self._context.get('default_is_advance_clearing', False) \
                and self._context.get('is_advance_clearing', False):
            reports = []
            self.filter_print_report(res, reports)
        return res
