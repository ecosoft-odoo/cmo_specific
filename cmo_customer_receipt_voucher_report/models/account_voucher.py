# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    comment_text = fields.Text(string='Comment Difference')
