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

    create_date_specific = fields.Char(
        string='Create Date',
        compute='_compute_create_date',
    )
    approve_date_specific = fields.Char(
        string='Approved Date',
        compute='_compute_approve_date',
    )

    @api.multi
    def _compute_create_date(self):
        for rec in self:
            t_timestamp = rec.create_date.split(" ")
            date = t_timestamp[0].split("-")
            t_time = t_timestamp[1].split(":")
            t_time[0] = int(t_time[0])+7
            rec.create_date_specific = "%s/%s/%s %s:%s" % (
                date[2], date[1], date[0], t_time[0], t_time[1])

    @api.multi
    def _compute_approve_date(self):
        for rec in self:
            t_timestamp = rec.approve_date.split(" ")
            date = t_timestamp[0].split("-")
            t_time = t_timestamp[1].split(":")
            t_time[0] = int(t_time[0])+7
            rec.approve_date_specific = "%s/%s/%s %s:%s" % (
                date[2], date[1], date[0], t_time[0], t_time[1])

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
