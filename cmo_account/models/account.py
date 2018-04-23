# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

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

    @api.multi
    def _compute_voucher_ref(self):
        for rec in self:
            voucher = rec.move_id.ref_voucher_id
            rec.voucher_number_cheque = voucher.number_cheque
            rec.voucher_date_value = voucher.date_value

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
