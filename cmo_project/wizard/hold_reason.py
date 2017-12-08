# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectHoldReason(models.TransientModel):
    _name = 'project.hold.reason'

    hold_reason = fields.Text(
        string='Hold Reason',
        required=True,
    )

    @api.multi
    def confirm_hold(self, context=None):
        self.ensure_one()
        Project = self.env['project.project']
        project = Project.browse(context.get('active_id'))
        project.hold_reason = self.hold_reason
        project.set_pending()
        return {'type': 'ir.actions.act_window_close'}
