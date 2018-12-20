# -*- coding: utf-8 -*-
from openerp import models, fields


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    employee_id = fields.Many2one(
        readonly=False,
    )
    amount_advanced = fields.Float(
        readonly=False,
    )
    number = fields.Char(
        readonly=False,
    )
