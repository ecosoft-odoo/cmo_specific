# -*- coding: utf-8 -*-
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    income_tax_form = fields.Text(
        string='Income Tax Form',
    )
