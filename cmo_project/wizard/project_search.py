# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectSearch(models.TransientModel):
    _name = 'project.search.wizard'

    project_id = fields.Many2one(
        'project.project',
        string="Project",
    )
    user_id = fields.Many2one(
        'res.users',
        string="User",
    )
    date_start = fields.Date(
        string="Start Date",
    )
    date_end = fields.Date(
        string="End Date",
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
        Project = self.env['project.project']
        project_ids = Project.search(dom).ids
        action = self.env.ref('project.open_view_project_all')
        result = action.read()[0]
        result.update({'domain': [('id', 'in', project_ids)],
                       'context': {}, })
        return result
