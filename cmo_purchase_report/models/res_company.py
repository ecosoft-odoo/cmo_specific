# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    check_billing_regulations = fields.Text(
        string='Check and billing regulations',
    )
