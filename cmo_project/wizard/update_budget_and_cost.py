# -*- coding: utf-8 -*-
from openerp import models, fields, api


class UpdateBudgetAndCostWizard(models.TransientModel):
    _name = 'update.budget.and.cost.wizard'

    update_type = fields.Selection(
        [('expense', 'Expense')],
        string='Update Type',
        required=True,
    )

    @api.multi
    def update_budget_and_cost(self):
        self.ensure_one()
        context = self._context.copy()
        active_ids = context.get('active_ids')
        active_model = context.get('active_model')
        if not (active_ids and active_model):
            return
        projects = self.env[active_model].browse(active_ids)
        if self.update_type == 'expense':
            projects._compute_expense()
