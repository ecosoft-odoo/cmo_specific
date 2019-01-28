# -*- coding: utf-8 -*-
from openerp import models, api


def filter_print_report(res, reports):
    action = []
    if res.get('toolbar', False) and \
            res.get('toolbar').get('print', False):
        for act in res.get('toolbar').get('print'):
            if act.get('report_name') in reports:
                action.append(act)
        res['toolbar']['print'] = action
    return res


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(HrExpenseExpense, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # HR Expense
        if not self._context.get('is_advance_clearing', False) and \
                not self._context.get('is_employee_advance', False) and \
                self._context.get('default_pay_to', False) != 'pettycash' and \
                not self._context.get('default_is_advance_clearing', False):
            reports = [
                u'cmo.hr.expense',
            ]
            filter_print_report(res, reports)
        # HR Advance
        elif self._context.get('default_is_employee_advance', False) and\
                self._context.get('is_employee_advance', False):
            reports = [
                u'cmo.hr.advance',
            ]
            filter_print_report(res, reports)
        # HR Advance Clearing
        elif self._context.get('default_is_employee_advance', False) is False \
                and self._context.get('default_is_advance_clearing', False) \
                and self._context.get('is_advance_clearing', False):
            reports = [
                u'cmo.hr.clearing',
            ]
            filter_print_report(res, reports)
        # HR Pettycash
        elif self._context.get('default_pay_to', False) == 'pettycash':
            reports = [
                u'cmo.hr.pettycash',
            ]
            filter_print_report(res, reports)
        return res
