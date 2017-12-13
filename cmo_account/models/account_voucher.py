# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('cheque_cash', 'Cheque (cash)'),
         ('cash', 'Cash'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        readonly=True, states={'draft': [('readonly', False)]},
    )
    company_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Company Bank Account',
        domain=lambda self:
        [('partner_id', '=', self.env.user.company_id.partner_id.id)],
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
