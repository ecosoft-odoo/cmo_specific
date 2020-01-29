# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']

    ref_invoice_id = fields.Many2one(
        'account.invoice',
        string='Ref Invoice',
        compute='_compute_ref_invoice_id',
    )
    ref_voucher_id = fields.Many2one(
        'account.voucher',
        string='Ref Voucher',
        compute='_compute_ref_voucher_id',
    )
    tax_detail_ids = fields.One2many(
        states={'posted': [('readonly', True)]}
    )
    approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Accounting Report Approver',
        copy=False,
        track_visibility='onchange',
    )
    approver_job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Accounting Report Approver Position',
        copy=False,
        track_visibility='onchange',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        approver = self.env.user.company_id.approver_id
        res.update({
            'approver_id': approver.id,
            'approver_job_id': approver.job_id.id
        })
        return res

    @api.multi
    def _compute_ref_invoice_id(self):
        Invoice = self.env['account.invoice']
        for rec in self:
            rec.ref_invoice_id = Invoice.search([('move_id', '=', rec.id)])

    @api.multi
    def _compute_ref_voucher_id(self):
        Voucher = self.env['account.voucher']
        for rec in self:
            rec.ref_voucher_id = Voucher.search([('move_id', '=', rec.id)])

    @api.multi
    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        message = '<div> &nbsp; &nbsp; &bull; <b>Status</b>: '\
            'Posted &rarr; Unposted</div>'
        for rec in self:
            rec.message_post(body=message)
        return res

    @api.multi
    def button_validate(self):
        res = super(AccountMove, self).button_validate()
        message = '<div> &nbsp; &nbsp; &bull; <b>Status</b>: '\
            'Unposted &rarr; Posted</div>'
        aml_obj = self.env['account.move.line']
        for rec in self:
            rec.message_post(body=message)
            if self.env['account.fiscalyear'].find(rec.date) != \
                    rec.period_id.fiscalyear_id.id:
                raise ValidationError(_('Date and period mismatch!'))
            aml_ids = aml_obj.search([('move_id', '=', rec.id),
                                     ('asset_id', '!=', False)])
            for aml_id in aml_ids:
                if aml_id.asset_id.code is False:
                    aml_id.asset_id.code = aml_id.move_id.name
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    voucher_number_cheque = fields.Char(
        string='Cheque Number',
        compute='_compute_voucher_ref',
        search='_search_voucher_number_cheque',
    )
    voucher_date_value = fields.Char(
        string='Value Date',
        compute='_compute_voucher_ref',
    )
    voucher_number_preprint = fields.Char(
        string='Preprint Number',
        related='move_id.ref_voucher_id.number_preprint',
    )
    invoices_ref = fields.Char(
        string='Invoices Ref',
        related='move_id.ref_voucher_id.invoices_ref',
    )

    voucher_payee = fields.Char(
        string='Payee',
        compute='_compute_voucher_ref',
        search='_search_voucher_payee',
    )
    cheque_status = fields.Selection(
        selection=[('canceled', 'Canceled'), ],
        compute='_compute_cheque_status',
        search='_search_cheque_status',
        string='Cheque Status',
        help='This is for show cheque status on bank intransit',
    )

    @api.multi
    def _compute_cheque_status(self):
        for rec in self:
            rec.cheque_status = rec.move_id.ref_voucher_id.cheque_status

    @api.model
    def _search_cheque_status(self, operator, value):
        context = self._context.copy()
        currency_id = context.get('currency_none_same_company_id', False)
        journal_id = context.get('journal_id', False)
        account_id = context.get('journal_default_account_id', False)
        domain = [
            ('reconcile_id', '=', False),
            ('credit', '>', 0),
            ('currency_id', '=', currency_id),
            ('journal_id', '=', journal_id),
            ('account_id', '=', account_id),
        ]
        lines = self.search(domain)
        if operator == '=':
            lines = lines.filtered(
                lambda l: l.move_id.ref_voucher_id.cheque_status == value)
        if operator == '!=':
            lines = lines.filtered(
                lambda l: l.move_id.ref_voucher_id.cheque_status != value)
        return [('id', 'in', lines.ids)]

    @api.multi
    def _compute_voucher_ref(self):
        for rec in self:
            voucher = rec.move_id.ref_voucher_id
            rec.voucher_number_cheque = voucher.number_cheque
            rec.voucher_date_value = voucher.date_value
            rec.voucher_payee = voucher.payee

    @api.model
    def _search_voucher_payee(self, operator, value):
        context = self._context.copy()
        currency_id = context.get('currency_none_same_company_id', False)
        journal_id = context.get('journal_id', False)
        account_id = context.get('journal_default_account_id', False)
        domain = [
            ('reconcile_id', '=', False),
            ('credit', '>', 0),
            ('currency_id', '=', currency_id),
            ('journal_id', '=', journal_id),
            ('account_id', '=', account_id)]
        lines = self.search(domain)
        if operator == 'ilike':
            lines = lines.filtered(
                lambda l:
                l.move_id.ref_voucher_id.payee is not False and
                value in l.move_id.ref_voucher_id.payee)
        if operator == 'not ilike':
            lines = lines.filtered(
                lambda l: l.move_id.ref_voucher_id.payee is False or
                (l.move_id.ref_voucher_id.payee is not False and
                 value not in l.move_id.ref_voucher_id.payee))
        if operator == '=':
            lines = lines.filtered(
                lambda l: value == l.move_id.ref_voucher_id.payee)
        if operator == '!=':
            lines = lines.filtered(
                lambda l: value != l.move_id.ref_voucher_id.payee)
        return [('id', 'in', lines.ids)]

    @api.model
    def _search_voucher_number_cheque(self, operator, value):
        context = self._context.copy()
        currency_id = context.get('currency_none_same_company_id', False)
        journal_id = context.get('journal_id', False)
        account_id = context.get('journal_default_account_id', False)
        domain = [
            ('reconcile_id', '=', False),
            ('credit', '>', 0),
            ('currency_id', '=', currency_id),
            ('journal_id', '=', journal_id),
            ('account_id', '=', account_id)]
        lines = self.search(domain)
        if operator == 'ilike':
            lines = lines.filtered(
                lambda l:
                l.move_id.ref_voucher_id.number_cheque is not False and
                value in l.move_id.ref_voucher_id.number_cheque)
        if operator == 'not ilike':
            lines = lines.filtered(
                lambda l: l.move_id.ref_voucher_id.number_cheque is False or
                (l.move_id.ref_voucher_id.number_cheque is not False and
                 value not in l.move_id.ref_voucher_id.number_cheque))
        if operator == '=':
            lines = lines.filtered(
                lambda l: value == l.move_id.ref_voucher_id.number_cheque)
        if operator == '!=':
            lines = lines.filtered(
                lambda l: value != l.move_id.ref_voucher_id.number_cheque)
        return [('id', 'in', lines.ids)]
