# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    prq_id = fields.Many2one(
        'purchase.prq',
        string='PRQ',
        index=True,
        ondelete='set null',
    )
