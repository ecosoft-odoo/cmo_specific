# -*- coding: utf-8 -*-
from openerp import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    start_date = fields.Date(string='Date of Start')
    probation_date = fields.Date(string='Date of Probation')
    end_date = fields.Date(string='Date of End')
