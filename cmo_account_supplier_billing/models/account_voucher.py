# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    supplier_billing_id = fields.Many2one(
        domain="[('state', '=', 'billed'), ('partner_id', '=', partner_id), \
                 ('billing_active', '=', True)]",
    )
