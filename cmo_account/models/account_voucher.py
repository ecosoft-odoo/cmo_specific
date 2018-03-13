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
    payee = fields.Char(
        string='Payee',
    )
    str_journal_items = fields.Char(
        compute='_compute_str_journal_items',
        string='Journal Items (String)',
    )

    @api.multi
    def onchange_partner_id(self, partner_id, journal_id, amount, currency_id,
                            ttype, date):
        res = super(AccountVoucher, self).onchange_partner_id(
            partner_id, journal_id, amount, currency_id, ttype, date)
        partner = self.env['res.partner'].browse(partner_id)
        res['value'].update({'payee': partner.name})
        return res

    @api.multi
    def _compute_str_journal_items(self):
        for voucher in self:
            journal_items = \
                voucher.line_ids.mapped('move_line_id').mapped('display_name')
            voucher.str_journal_items = ', '.join(sorted(journal_items))
