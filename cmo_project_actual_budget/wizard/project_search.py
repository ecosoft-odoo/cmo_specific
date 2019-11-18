# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectSearch(models.TransientModel):
    _inherit = 'project.search.wizard'

    actual_from_date = fields.Date(
        string='Budget Per Year From Date',
    )
    actual_to_date = fields.Date(
        string='Budget Per Year To Date',
    )

    @api.multi
    def search_project(self):
        res = super(ProjectSearch, self).search_project()
        res['context'].update({
            'actual_from_date': self.actual_from_date,
            'actual_to_date': self.actual_to_date,
            'show_actual_budget': True, })
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(ProjectSearch, self).default_get(fields_list)
        Fiscalyear = self.env['account.fiscalyear'].find()
        fiscalyear = self.env['account.fiscalyear'].browse(Fiscalyear)
        if 'actual_from_date' in fields_list:
            res.update({'actual_from_date': fiscalyear.date_start})
        if 'actual_to_date' in fields_list:
            res.update({'actual_to_date': fiscalyear.date_stop})
        return res
