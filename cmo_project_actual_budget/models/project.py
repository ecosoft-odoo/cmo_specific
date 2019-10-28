# -*- coding: utf-8 -*-
# from lxml import etree
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare

# TODO: foreign key use, idex and ondelete


class ProjectProject(models.Model):
    _inherit = 'project.project'

    has_actual_budget = fields.Boolean(
        string='Actual Budget',
        default=False,
    )
    actual_budget_ids = fields.One2many(
        'project.actual.budget',
        'project_id',
        string='Actual Budgets',
        copy=False,
    )
    actual_budget = fields.Float(
        string='Actual Budget',
        compute='_compute_actual_budget',
    )

    @api.multi
    def _compute_actual_budget(self):
        for rec in self:
            actual_from_date = rec._context.get('actual_from_date')
            actual_to_date = rec._context.get('actual_to_date')
            if not rec.has_actual_budget or \
                    not (actual_from_date or actual_to_date):
                rec.actual_budget = rec.project_budget
            else:
                domain = [('project_id', '=', rec.id)]
                if actual_from_date:
                    domain += [('to_date', '>=', actual_from_date)]
                if actual_to_date:
                    domain += [('to_date', '<=', actual_to_date)]
                actual = self.env['project.actual.budget'].search(domain)
                actual_budget = 0.0
                if actual:
                    actual_budget = sum(actual.mapped('amount'))
                else:
                    actual = self.env['project.actual.budget'].search(
                        [('project_id', '=', rec.id)], order='to_date')
                    if actual:
                        if actual_to_date and \
                           actual_to_date < actual[0].to_date:
                            actual_budget = rec.project_budget
                        if actual_from_date and \
                           actual_from_date > actual[-1].to_date:
                            actual_budget = actual[-1].amount
                rec.actual_budget = actual_budget


class ProjectActualBudget(models.Model):
    _name = 'project.actual.budget'
    _description = 'Project Actual Budgets'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        index=True,
        ondelete='cascade',
    )
    to_date = fields.Date(
        string='Up to date',
        required=True,
        help="Up to date that the actual amount reach",
    )
    amount = fields.Float(
        string='Amount',
        required=True,
        help="Accumulated amount up to specified date",
    )
