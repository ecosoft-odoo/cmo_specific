# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectSearch(models.TransientModel):
    _name = 'project.search.wizard'

    project_name = fields.Char(
        string='Project Name',
    )
    project_code = fields.Char(
        string='Project Code',
    )
    project_place = fields.Char(
        string='Project Place',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Create By',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
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
    agency_partner_id = fields.Many2one(
        'res.partner',
        string='Agency',
    )
    stage = fields.Selection(
        [('draft', 'Draft'),
         ('validate', 'Validate'),
         ('open', 'In Progress'),
         ('ready_billing', 'Ready to Billing'),
         ('invoiced', 'Invoiced'),
         ('paid', 'Paid'),
         ('cancelled', 'Incompleted'),
         ('pending', 'Hold'),
         ('close', 'Completed')]
    )
    close_reason = fields.Selection(
        [('close', 'Completed'),
         # ('it_close', 'IT Close Project'),
         ('reject', 'Reject'),
         ('lost', 'Lost'),
         ('cancel', 'Cancelled'),
         ('terminate', 'Terminated'), ],
        string='Close Reason',
    )

    client_type_id = fields.Many2one(
        'project.client.type',
        string='Client Type',
    )
    obligation_id = fields.Many2one(
        'project.obligation',
        string='Obligation',
    )
    project_manager_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
    )
    designer_id = fields.Many2one(
        'hr.employee',
        string='Designer',
    )
    procurement_id = fields.Many2one(
        'hr.employee',
        string='Procurement',
    )
    production_id = fields.Many2one(
        'hr.employee',
        string='Production',
    )
    creative_id = fields.Many2one(
        'hr.employee',
        string='Creative',
    )
    graphic_id = fields.Many2one(
        'hr.employee',
        string='Graphic',
    )
    producer_id = fields.Many2one(
        'hr.employee',
        string='Producer',
    )
    asst_production_id = fields.Many2one(
        'hr.employee',
        string='Asst. Production',
    )

    @api.multi
    def search_project(self):
        self.ensure_one()
        dom_team = []
        pos = []
        if self.project_manager_id:
            dom_team += [('employee_id', '=', self.project_manager_id.id)]
            pos += [self.env.ref('cmo_project.project_position_1', False).id]
        if self.designer_id:
            dom_team += [('employee_id', '=', self.designer_id.id)]
            pos += [self.env.ref('cmo_project.project_position_2', False).id]
        if self.procurement_id:
            dom_team += [('employee_id', '=', self.procurement_id.id)]
            pos += [self.env.ref('cmo_project.project_position_3', False).id]
        if self.production_id:
            dom_team += [('employee_id', '=', self.production_id.id)]
            pos += [self.env.ref('cmo_project.project_position_4', False).id]
        if self.creative_id:
            dom_team += [('employee_id', '=', self.creative_id.id)]
            pos += [self.env.ref('cmo_project.project_position_5', False).id]
        if self.graphic_id:
            dom_team += [('employee_id', '=', self.graphic_id.id)]
            pos += [self.env.ref('cmo_project.project_position_6', False).id]
        if self.producer_id:
            dom_team += [('employee_id', '=', self.producer_id.id)]
            pos += [self.env.ref('cmo_project.project_position_7', False).id]
        if self.asst_production_id:
            dom_team += [('employee_id', '=', self.asst_production_id.id)]
            pos += [self.env.ref('cmo_project.project_position_8', False).id]
        dom_team += [('position_id', 'in', pos)]
        Team = self.env['project.team.member']
        team_ids = Team.search(dom_team)
        project_id = team_ids.mapped('project_id.id')
        where_date = ''
        # condition Find not found
        if not project_id and pos:
            action = self.env.ref('project.open_view_project_all')
            result = action.read()[0]
            result.update({'domain': [('id', 'in', project_id)],
                           'context': {}, })
        else:
            dom = [('id', 'in', project_id)]
            if not project_id:
                dom = []
            if self.project_code:
                dom += [('code', 'like', self.project_code)]
            if self.project_name:
                dom += [('name', 'like', self.project_name)]
            if self.project_place:
                dom += [('project_place', 'like', self.project_place)]
            if self.user_id:
                dom += [('user_id', '=', self.user_id.id)]
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
            if self.close_reason:
                dom += [('close_reason', '=', self.close_reason)]
            if self.client_type_id:
                dom += [('client_type_id', '=', self.client_type_id.id)]
            if self.obligation_id:
                dom += [('obligation_id', '=', self.obligation_id.id)]
            if self.date_start and self.date_end:
                where_date = "(aaa.date_start between '%s' and '%s' \
                    or pp.date between '%s' and '%s' \
                    or aaa.date_start <= '%s' and pp.date >= '%s' \
                    or aaa.date_start >= '%s' and pp.date <= '%s')" % \
                    (self.date_start, self.date_end, self.date_start,
                     self.date_end, self.date_start, self.date_end,
                     self.date_start, self.date_end)
            elif self.date_start:
                where_date = "(pp.date >= '%s')" % (self.date_start)
            elif self.date_end:
                where_date = "(aaa.date_start <= '%s')" % (self.date_end)
            Project = self.env['project.project']
            project_ids = Project.search(dom).ids
            if project_ids and where_date:
                where_date = 'and ' + where_date
                self._cr.execute("""
                    select pp.id
                    from project_project pp
                    join account_analytic_account aaa on aaa.id =
                        pp.analytic_account_id
                    where pp.id in %s
                """ + where_date, (tuple(project_ids), ))
                project_ids = self._cr.fetchall()
            action = self.env.ref('project.open_view_project_all')
            result = action.read()[0]
            result.update({'domain': [('id', 'in', project_ids)],
                           'context': {}, })
        return result

    @api.model
    def default_get(self, fields_list):
        res = super(ProjectSearch, self).default_get(fields_list)
        Fiscalyear = self.env['account.fiscalyear'].find()
        fiscalyear = self.env['account.fiscalyear'].browse(Fiscalyear)
        if 'date_start' in fields_list:
            res.update({'date_start': fiscalyear.date_start})
        if 'date_end' in fields_list:
            res.update({'date_end': fiscalyear.date_stop})
        return res
