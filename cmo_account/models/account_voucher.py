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
        change_default=1,
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
    invoices_ref = fields.Char(
        string='Invoices Ref',
        compute='_compute_invoices_ref',
    )
    note = fields.Text(
        string='Company Bank Account',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    validate_user_id = fields.Many2one(
        'res.partner',
        string='Verify By',
    )
    approved_user_id = fields.Many2one(
        'res.partner',
        string='Approved By',
    )
    number_preprint = fields.Char(
        required=True
    )
    date_value = fields.Date(
        string='Payment Date',
    )
    cheque_status = fields.Selection(
        selection=[('canceled', 'Canceled'), ],
        string='Cheque Status',
    )
    approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approver',
        copy=False,
        track_visibility='onchange',
    )
    approver_job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Approver Position',
        copy=False,
        track_visibility='onchange',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountVoucher, self).default_get(fields)
        approver = self.env.user.company_id.approver_id
        res.update({
            'approver_id': approver.id,
            'approver_job_id': approver.job_id.id
        })
        return res

    @api.multi
    def _compute_invoices_ref(self):
        for rec in self:
            rec.invoices_ref = ', '.join(rec.line_ids.filtered('reference').
                                         mapped('reference'))

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


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    reference = fields.Char(
        related='invoice_id.number_preprint',
        readonly=True,
        store=True,
    )
