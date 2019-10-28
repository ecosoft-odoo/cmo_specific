# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectSearch(models.TransientModel):
    _inherit = 'project.search.wizard'

    actual_from_date = fields.Date(
        string='Actual Budget From Date',
    )
    actual_to_date = fields.Date(
        string='Actual Budget To Date',
    )

    @api.multi
    def search_project(self):
        res = super(ProjectSearch, self).search_project()
        res['context'].update({
            'actual_from_date': self.actual_from_date,
            'actual_to_date': self.actual_to_date,
            'show_actual_budget': True, })
        return res
