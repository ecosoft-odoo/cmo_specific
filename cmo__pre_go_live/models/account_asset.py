# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    operating_unit_id = fields.Many2one(
        readonly=False,
    )
