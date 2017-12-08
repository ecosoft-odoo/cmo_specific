# -*- coding: utf-8 -*-
from openerp import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    active = fields.Boolean(
        string='Active',
        default=True,
    )
    show = fields.Boolean(
        string='Show',
        default=True,
    )
