# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    prq_id = fields.Many2one(
        'purchase.prq',
        string='PRQ',
        index=True,
        ondelete='set null',
    )

    @api.multi
    def write(self, vals):
        for invoice in self:
            if vals.get('state', False) == 'paid':
                invoice.prq_id.state = 'done'
        res = super(AccountInvoice, self).write(vals)
        return res
