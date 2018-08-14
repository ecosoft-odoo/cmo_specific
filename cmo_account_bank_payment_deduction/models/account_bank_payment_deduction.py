# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools import float_compare


class AccountBankPaymentMultipleReconcile(models.Model):
    _name = 'account.bank.payment.multiple.reconcile'
    _description = 'Account Bank Payment Multiple Reconcile'

    account_id = fields.Many2one(
        'account.account',
        string='Reconcile Account',
        domain=[('type', 'not in', ['view', 'closed']),
                ('reconcile', '!=', True)],
        required=True,
    )
    amount = fields.Float(
        string='Amount',
        digits_compute=dp.get_precision('Account'),
        required=True,
    )
    note = fields.Char(
        string='Comment',
        required=True,
    )
    bank_payment_id = fields.Many2one(
        'account.bank.payment',
        string='Related Bank Payment',
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )


class AccountBankPayment(models.Model):
    _inherit = 'account.bank.payment'

    multiple_reconcile_ids = fields.One2many(
        'account.bank.payment.multiple.reconcile',
        'bank_payment_id',
        string='Reconcile Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    writeoff_amount = fields.Float(
        string="Writeoff Amount",
        readonly=True,
        compute="_compute_writeoff_amount",
        help="Computed as the difference between the amount\
        stated in the voucher and the sum of allocation\
        on the voucher lines.",
    )
    payment_difference_amount = fields.Float(
        string="Difference Amount",
        readonly=True,
        compute="_compute_writeoff_amount",
        help="Computed as the difference between the amount\
        stated in the voucher and the sum of allocation\
        on the voucher lines.",
    )
    total_amount = fields.Float(
        string="Computed Total Amount",
        copy=False,
    )
    manual_total_amount = fields.Float(
        string="Total Amount",
        readonly=True,
        default=0.0,
        states={'draft': [('readonly', False)]},
        required=True,
        copy=False,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
    )

    @api.multi
    def validate_bank_payment(self):
        for payment in self:
            if float_compare(payment.writeoff_amount, 0.0, 2) != 0:
                raise ValidationError(
                    _('Writeoff Amount must be 0.0 to validate!'))
        res = super(AccountBankPayment, self).validate_bank_payment()
        return res

    @api.multi
    @api.depends('manual_total_amount')
    def _compute_bank_payment(self):
        res = super(AccountBankPayment, self)._compute_bank_payment()
        for payment in self:
            payment.total_amount = payment.manual_total_amount
        return res

    @api.multi
    @api.depends(
        'total_amount',
        'multiple_reconcile_ids',
        'multiple_reconcile_ids.amount'
    )
    def _compute_writeoff_amount(self):
        for payment in self:
            total = 0.0
            currency_none_same_company_id = False
            if payment.company_id.currency_id != payment.currency_id:
                currency_none_same_company_id = payment.currency_id.id
            for line in payment.bank_intransit_ids:
                if currency_none_same_company_id:
                    total += line.amount_currency
                else:
                    total += line.credit
            writeoffline_amount = 0.0
            if payment.multiple_reconcile_ids:
                writeoffline_amount =\
                    sum([l.amount for l in payment.multiple_reconcile_ids])
            payment.payment_difference_amount = payment.total_amount - total
            payment.writeoff_amount = (payment.total_amount -
                                       writeoffline_amount -
                                       total)

    @api.model
    def _create_writeoff_move_line_hook(self, move):
        super(AccountBankPayment, self)._create_writeoff_move_line_hook(move)
        if self.payment_difference_amount != 0.0:
            MoveLine = self.env['account.move.line']
            if self.payment_difference_amount != 0.0 and \
                    self.multiple_reconcile_ids:
                for writeofline in self.multiple_reconcile_ids:
                    move_line_val = \
                        self._prepare_writeoff_move_line(writeofline)
                    move_line_val['move_id'] = move.id
                    MoveLine.create(move_line_val)
        return True

    @api.model
    def _do_reconcile(self, to_reconcile_lines):
        if self.payment_difference_amount != 0.0 and \
                self.multiple_reconcile_ids:
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile_partial(type='manual')
            return True
        else:
            return super(AccountBankPayment,
                         self)._do_reconcile(to_reconcile_lines)

    @api.onchange('writeoff_amount')
    def onchange_writeoff_amount(self):
        for payment in self:
            if payment.writeoff_amount == 0.0:
                payment.multiple_reconcile_ids = [(6, 0, [])]

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, payment, total_credit, total_amount_currency):
        vals = super(AccountBankPayment, self).\
            _prepare_counterpart_move_lines_vals(payment, total_credit,
                                                 total_amount_currency)
        if self.payment_difference_amount != 0.0 and \
                self.multiple_reconcile_ids:
            vals['credit'] = self.total_amount
        return vals

    @api.model
    def _prepare_writeoff_move_line(self, writeofline):
        credit = 0.0
        debit = 0.0
        if writeofline.amount > 0.0:
            debit = abs(writeofline.amount)
        else:
            credit = abs(writeofline.amount)
        return {
            'name': writeofline.note,
            'credit': credit,
            'debit': debit,
            'account_id': writeofline.account_id.id,
            'partner_id': False,
            'currency_id': False,
            'amount_currency': False,
            'analytic_account_id': writeofline.analytic_id and
            writeofline.analytic_id.id or False,
        }
