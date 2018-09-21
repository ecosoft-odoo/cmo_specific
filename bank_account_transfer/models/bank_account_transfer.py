# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class BankAccountTransfer(models.Model):
    _name = 'bank.account.transfer'

    name = fields.Char(
        string='Name',
        size=64,
        readonly=True,
        default='',
        copy=False,
    )
    transfer_line_ids = fields.One2many(
        'bank.account.transfer.line',
        'bank_transfer_id',
        string='Transfer Line',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date = fields.Date(
        string='Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    from_account_id = fields.Many2one(
        'account.account',
        string='Bank Account',
        domain="[('type', '!=', 'view')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    to_account_id = fields.Many2one(
        'account.account',
        string='Bank Account',
        domain="[('type', '!=', 'view')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fee_account_id = fields.Many2one(
        'account.account',
        string='Bank Account',
        domain="[('type', '!=', 'view')]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Text(
        string='Notes',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancel')],
        string='Status',
        default='draft',
        readonly=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('code', '=', 'BT')],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id,
        states={'draft': [('readonly', False)]},
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    deduct_from = fields.Many2one(
        'account.account',
        string='Deduct From',
        domain="[('type', '!=', 'view')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    move_ids = fields.One2many(
        'account.move.line',
        related='move_id.line_id',
        string='Journal Items',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_transfer = fields.Float(
        string='Transfer Amount',
        compute='_compute_transfer_amount',
        readonly=True,
    )
    amount_fee = fields.Float(
        string='Fee',
        compute='_compute_fee',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
        readonly=True,
    )

    @api.depends('transfer_line_ids')
    @api.multi
    def _compute_transfer_amount(self):
        for rec in self:
            rec.amount_transfer = sum(
                rec.transfer_line_ids.mapped('transfer_amount'))

    @api.depends('transfer_line_ids')
    @api.multi
    def _compute_fee(self):
        for rec in self:
            rec.amount_fee = sum(
                rec.transfer_line_ids.mapped('fee'))

    @api.depends('amount_transfer', 'amount_fee')
    @api.multi
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.amount_transfer + rec.amount_fee

    @api.model
    def _prepare_account_move_vals(self, transfer):
        date = transfer.date
        Period = self.env['account.period']
        period_ids = Period.find(dt=date)
        move_vals = {
            'journal_id': transfer.journal_id.id,
            'date': date,
            'period_id': period_ids[0].id,
            'name': transfer.name,
            'ref': transfer.name,
        }
        return move_vals

    @api.model
    def _prepare_credit_line_vals(self, transfer,
                                  company_amount, company_currency):
        assert (company_amount > 0), 'Credit must have a value'
        return {
            'name': _('Bank Transfer - Ref. %s') % transfer.name,
            'credit': company_amount,
            'debit': 0.0,
            'account_id': self.from_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.model
    def _prepare_dedit_line_vals(self, transfer,
                                 company_amount, company_currency):
        assert (company_amount > 0), 'Credit must have a value'
        return {
            'name': _('Bank Transfer - Ref. %s') % transfer.name,
            'credit': 0.0,
            'debit': company_amount,
            'account_id': self.to_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.model
    def _prepare_fee_credit_move_lines_vals(
            self, transfer, total_fee, company_currency):
        return {
            'name': _('Bank Transfer %s') % transfer.name,
            'debit': 0.0,
            'credit': total_fee,
            'account_id': self.deduct_from.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.model
    def _prepare_fee_debit_move_lines_vals(
            self, transfer, total_fee, company_currency):
        return {
            'name': _('Bank Transfer %s') % transfer.name,
            'debit': total_fee,
            'credit': 0.0,
            'account_id': self.fee_account_id.id,
            'currency_id':
                self.currency_id.id
                if company_currency != self.currency_id else False,
        }

    @api.multi
    def action_bank_transfer(self):
        Move = self.env['account.move']
        MoveLine = self.env['account.move.line']
        company_currency = self.env.user.company_id.currency_id
        for transfer in self:
            if not transfer.transfer_line_ids:
                raise ValidationError(_('No lines!'))
            if not transfer.transfer_line_ids.transfer_amount:
                raise ValidationError(_('No Transfer Amount!'))
            if transfer.from_account_id == transfer.to_account_id:
                raise ValidationError(_('From Account and To Account \
                                can not be the same account. Please Change!!'))
            if sum(transfer.transfer_line_ids.mapped('fee')) and \
                    not transfer.fee_account_id:
                raise ValidationError(_('No Fee Account!'))

            refer_type = 'bank_payment'
            doctype = transfer.env['res.doctype'].get_doctype(refer_type)
            fiscalyear_id = transfer.env['account.fiscalyear'].find()
            transfer = transfer.with_context(doctype_id=doctype.id,
                                             fiscalyear_id=fiscalyear_id)
            name = transfer.env['ir.sequence'].next_by_code(
                'bank.account.transfer')
            transfer.write({'name': name})

            move_vals = self._prepare_account_move_vals(transfer)
            move = Move.create(move_vals)
            trans_currency = transfer.currency_id
            total_credit = 0.0
            total_fee = 0.0
            for line in transfer.transfer_line_ids:
                company_amount = trans_currency.compute(line.transfer_amount,
                                                        company_currency)
                company_fee = trans_currency.compute(line.fee,
                                                     company_currency)
                total_credit += company_amount
                total_fee += company_fee
                credit_line_vals = self._prepare_credit_line_vals(
                    transfer, company_amount, company_currency)
                dedit_line_vals = self._prepare_dedit_line_vals(
                    transfer, company_amount, company_currency)
                credit_line_vals['move_id'] = move.id
                dedit_line_vals['move_id'] = move.id
                MoveLine.create(credit_line_vals)
                MoveLine.create(dedit_line_vals)

            fee_debit_vals = self._prepare_fee_debit_move_lines_vals(
                      transfer, total_fee, company_currency)
            fee_credit_vals = self._prepare_fee_credit_move_lines_vals(
                      transfer, total_fee, company_currency)
            fee_debit_vals['move_id'] = move.id
            fee_credit_vals['move_id'] = move.id
            MoveLine.create(fee_debit_vals)
            MoveLine.create(fee_credit_vals)
            move.post()
            transfer.write({'state': 'done',
                           'move_id': move.id,
                            })
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})


class BankAccountTransferLine(models.Model):
    _name = 'bank.account.transfer.line'

    bank_transfer_id = fields.Many2one(
        'bank.account.transfer',
        string='Bank Account Transfer',
    )
    date_transfer = fields.Date(
        string='Date',
        required=True,
    )
    transfer_amount = fields.Float(
        string='Transfer Amount',
        digits=dp.get_precision('Account'),
        required=True,
    )
    fee = fields.Float(
        string='Fee',
        digits=dp.get_precision('Account'),
        readonly=False,
    )
