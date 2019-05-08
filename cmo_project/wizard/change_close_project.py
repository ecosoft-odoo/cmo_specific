# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ChangeCloseProject(models.TransientModel):
    _name = 'change.close.project'

    close_project = fields.Boolean(
        string='Close Project by Accounting',
    )

    @api.model
    def default_get(self, fields):
        res = super(ChangeCloseProject, self).default_get(fields)
        active_id = self._context.get('active_id')
        project = self.env['project.project'].browse(active_id)
        res['close_project'] = project.close_project
        return res

    @api.multi
    def change_close_project(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        project = self.env['project.project'].browse(active_id)
        project.write({'close_project': self.close_project})
        return True
