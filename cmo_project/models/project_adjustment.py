# -*- coding: utf-8 -*-

from openerp import fields, models, api
from openerp.exceptions import ValidationError


class ProjectAdjustment(models.Model):
    _name = 'project.adjustment'

    name = fields.Char(
        string='Description',
        required=True,
    )
    amount = fields.Float(
        string='Amount',
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project Ref',
        ondelete='cascade',
        index=True,
    )
