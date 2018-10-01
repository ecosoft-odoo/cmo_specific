# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectSearch(models.TransientModel):
    _name = 'project.search.wizard'

    project_id = fields.Many2one(
        'project.project',
        string="Project Name",
    )
    user_id = fields.Many2one(
        'res.users',
        string="Project Manager",
    )
    date_start = fields.Date(
        string="Start Date",
    )
    date_end = fields.Date(
        string="End Date",
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Department',
    )
    project_type_id = fields.Many2one(
        'project.type',
        string='Project Type',
    )
    project_from_id = fields.Many2one(
        'project.from',
        string='Project From',
    )
    function_id = fields.Many2one(
        'project.function',
        string='Function',
    )
    project_budget_from = fields.Char(
        string='Budget From',
    )
    project_budget_to = fields.Char(
        string='Budget To'
    )
    location_id = fields.Many2one(
        'project.location',
        string='Location',
    )
    stage = fields.Selection(
        [('draft', 'Draft'),
         ('validate', 'Validate'),
         ('open', 'In Progress'),
         ('ready_billing', 'Ready to Billing'),
         ('pending', 'Hold'),
         ('close', 'Completed')]
    )
    client_type_id = fields.Many2one(
        'project.client.type',
        string='Client Type',
    )
    obligation_id = fields.Many2one(
        'project.obligation',
        string='Obligation',
    )

    @api.multi
    def search_project(self):
        self.ensure_one()
        dom = []
        if self.project_id:
            dom += [('id', '=', self.project_id.id)]
        if self.user_id:
            dom += [('user_id', '=', self.user_id.id)]
        if self.date_start:
            dom += [('date_start', '>=', self.date_start)]
        if self.date_end:
            dom += [('date', '<=', self.date_end)]
        if self.operating_unit_id:
            dom += [('operating_unit_id', '=', self.operating_unit_id.id)]
        if self.project_type_id:
            dom += [('project_type_id', '=', self.project_type_id.id)]
        if self.project_from_id:
            dom += [('project_from_id', '=', self.project_from_id.id)]
        if self.function_id:
            dom += [('function_id', '=', self.function_id.id)]
        if self.project_budget_from:
            dom += [('project_budget', '>=', self.project_budget_from)]
        if self.project_budget_to:
            dom += [('project_budget', '<=', self.project_budget_to)]
        if self.location_id:
            dom += [('location_id', '=', self.location_id.id)]
        if self.stage:
            dom += [('state', '=', self.stage)]
        if self.client_type_id:
            dom += [('client_type_id', '=', self.client_type_id.id)]
        if self.obligation_id:
            dom += [('obligation_id', '=', self.obligation_id.id)]
        Project = self.env['project.project']
        project_ids = Project.search(dom).ids
        action = self.env.ref('project.open_view_project_all')
        result = action.read()[0]
        result.update({'domain': [('id', 'in', project_ids)],
                       'context': {}, })
        return result
