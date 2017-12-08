# -*- coding: utf-8 -*-

from openerp import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def _xls_cost_control_sheet_fields(self):
        return [
            'name', 'price_in_contract', 'estimate_cost', 'percent_margin'
        ]

    @api.model
    def _xls_cost_control_sheet_template(self):
        """
        Template updates

        """
        return {}
