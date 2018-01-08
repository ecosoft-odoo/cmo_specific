# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref_invoice_id = fields.Many2one(
        'account.inoice',
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
    )
    voucher_date_value = fields.Char(
        string='Value Date',
        compute='_compute_voucher_ref',
    )

    @api.multi
    def _compute_voucher_ref(self):
        for rec in self:
            voucher = rec.move_id.ref_voucher_id
            rec.voucher_number_cheque = voucher.number_cheque
            rec.voucher_date_value = voucher.date_value
