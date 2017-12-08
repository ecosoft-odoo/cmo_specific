# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProjectCloseReason(models.TransientModel):
    _name = 'project.close.reason'

    close_reason = fields.Selection(
        string='Close Reason',
        selection="_get_close_reason_list",
    )
    lost_by_id = fields.Many2one(
        'res.partner',
        string='Lost By',
        domain=[('category_id', 'like', 'Competitor'), ],
    )
    lost_reason_id = fields.Many2one(
        'project.lost.reason',
        string='Lost Reason',
    )
    reject_reason_id = fields.Many2one(
        'project.reject.reason',
        string='Reject Reason',
    )

    @api.multi
    def confirm_close(self, context=None):
        self.ensure_one()
        Project = self.env['project.project']
        project = Project.browse(context.get('active_id'))
        project.write({
            'close_reason': self.close_reason,
        })
        if self.close_reason == 'lost':
            project.write({
                'lost_reason_id': self.lost_reason_id.id,
                'lost_by_id': self.lost_by_id.id,
            })
            project.set_cancel()
        elif self.close_reason == 'reject':
            project.write({
                'reject_reason_id': self.reject_reason_id.id,
            })
            project.set_cancel()
        elif self.close_reason == 'cancel' or self.close_reason == 'terminate':
            project.set_cancel()
        elif self.close_reason == 'close':
            project.set_done()
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def _get_close_reason_list(self):
        Project = self.env['project.project']
        context = self.env.context
        project_id = context.get('active_ids', False)
        vals = []
        if project_id:
            project = Project.browse(project_id[0])
            if project.state == "draft" or project.state == "validate":
                vals = [
                    ('reject', 'Reject'),
                    ('lost', 'Lost'),
                    ('cancel', 'Cancelled'),
                ]
            elif (project.state == "open") or \
                 (project.state == "ready_billing") or \
                 (project.state == "invoices"):
                vals = [
                    ('cancel', 'Cancelled'),
                    ('terminate', 'Terminated'),
                ]
            elif (project.state == "received"):
                vals = [
                    ('close', 'Completed'),
                ]
        return vals
