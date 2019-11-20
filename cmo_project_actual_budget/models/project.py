# -*- coding: utf-8 -*-
from lxml import etree
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare

# TODO: foreign key use, idex and ondelete


class ProjectProject(models.Model):
    _inherit = 'project.project'

    has_actual_budget = fields.Boolean(
        string='Budget Per Year',
        default=False,
    )
    actual_budget_ids = fields.One2many(
        'project.actual.budget',
        'project_id',
        string='Budget Per Years',
        copy=False,
    )
    actual_budget = fields.Float(
        string='Budget Per Year',
        compute='_compute_actual_budget',
    )

    @api.constrains('actual_budget_ids')
    def _check_actual_budget_ids(self):
        for rec in self:
            to_dates = self.actual_budget_ids.mapped('to_date')
            not_valid_dates = [
                x for x in to_dates if not (rec.date_start <= x <= rec.date)]
            if not_valid_dates:
                raise ValidationError(_('Budget per year is not valid.'))

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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(ProjectProject, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        if 'actual_budget' in fields:
            for line in res:
                if '__domain' in line:
                    line['actual_budget'] = \
                        sum(self.search(line['__domain'])
                            .mapped('actual_budget'))
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(ProjectProject, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'tree':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field")
            for node in nodes:
                node.set("bg_color", "yellow:has_actual_budget is True")
            res['arch'] = etree.tostring(doc)
        return res


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
