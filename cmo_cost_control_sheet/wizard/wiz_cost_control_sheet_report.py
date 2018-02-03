# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class WizCostControlSheetReport(models.TransientModel):

    _name = 'wiz.cost.control.sheet.report'
    _description = 'Cost Control Sheet report'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
    )

    @api.multi
    def xls_export(self):
        self.ensure_one()
        project_obj = self.env['project.project']
        if not project_obj.search([]):
            raise UserError(
                _('Configuration Error'),
                _("No Project defined!"))
        datas = {
            'model': 'project.project',
            'project_id': self.project_id.id,
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'cost.control.sheet.xls',
                'datas': datas}
