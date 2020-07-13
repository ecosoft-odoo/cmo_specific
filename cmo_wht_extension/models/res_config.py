# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    income_tax_form = fields.Text(
        string='Income Tax Form',
        related='company_id.income_tax_form',
        help='Ex: {"pnd1": "XSCM", "pnd3": "XPCM", "pnd53": "XCCM"}',
        required=True,
    )
