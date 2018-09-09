# -*- coding: utf-8 -*-
from openerp import models, fields


class HRExpenseExpese(models.Model):
    _inherit = "hr.expense.expense"

    require_prq = fields.Boolean(
        string='Require PRQ',
    )
