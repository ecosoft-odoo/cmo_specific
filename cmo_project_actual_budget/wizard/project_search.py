# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectSearch(models.TransientModel):
    _inherit = 'project.search.wizard'

    actual_to_date = fields.Date(
        string='Actual Budget To Date',
    )

    @api.multi
    def search_project(self):
        self.env.user.write({'search_project_to_date': self.actual_to_date})
        res = super(ProjectSearch, self).search_project()
        res['context'].update({'show_actual_budget': True})
        return res
