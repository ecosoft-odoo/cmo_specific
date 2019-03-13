# -*- coding: utf-8 -*-
from openerp import models, api, fields


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

    has_wht_amount = fields.Float(
        string='WHT amount',
        compute='_compute_cal_wht',
    )

    @api.multi
    def _compute_cal_wht(self):
        self._cr.execute(
            """
                select expense.id, sum(
                    line_exp.unit_amount * line_exp.unit_quantity * at.amount)
                    as has_wht_amount
                from hr_expense_expense expense
                join hr_expense_line line_exp
                    on expense.id = line_exp.expense_id
                join expense_line_tax_rel elt
                    on line_exp.id = elt.expense_line_id
                join account_tax at on elt.tax_id = at.id
                where at.is_wht is true and expense.id in %s
                group by expense.id
            """, (tuple(self.ids), ))
        result = self._cr.fetchall()
        for rec in self:
            amount = dict(result).get(rec.id, False)
            rec.has_wht_amount = amount

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(HrExpenseExpense, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # print report not show from active model is project.project
        if self._context.get('active_model') == 'project.project':
            reports = []
            filter_print_report(res, reports)
            return res
        # --
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
