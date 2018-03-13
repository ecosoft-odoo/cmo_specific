# -*- coding: utf-8 -*-
from openerp import models, fields


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    access_all_operating_unit = fields.Boolean(
        string='Access All Operating Unit',
    )
