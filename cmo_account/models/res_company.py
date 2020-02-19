# -*- coding: utf-8 -*-
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Accounting Report Approver",
    )
