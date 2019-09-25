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
            if not rec.has_actual_budget or \
                    not self.env.user.search_project_to_date:
                rec.actual_budget = rec.project_budget
            else:
                actual = self.env['project.actual.budget'].search(
                    [('project_id', '=', rec.id),
                     ('to_date', '<=', self.env.user.search_project_to_date)],
                    order='to_date desc', limit=1)
                rec.actual_budget = actual and actual.amount or 0.0


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
