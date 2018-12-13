# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ReconcileUnbilledItems(models.TransientModel):
    _name = 'reconcile.unbilled.items'

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        default=lambda self: self._get_journal_id(),
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Reconcile With',
        required=True,
        domain=[('account_id.reconcile', '=', True)],
    )

    @api.model
    def _get_journal_id(self):
        Journal = self.env['account.journal']
        return Journal.search([('code', '=', 'JV')], limit=1).id

    @api.model
    def view_init(self, fields_list):
        invoice_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.state not in ('open', 'paid') or \
                invoice.type not in ('out_invoice', 'out_refund'):
            raise ValidationError(
                _('Only open customer invoice allowed!'))

    @api.multi
    def action_create_journal_entry(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_journal_line')
        view = self.env.ref('account.view_move_form')
        result = action.read()[0]
        result.update({'view_mode': 'form',
                       'target': 'current',
                       'view_id': view.id,
                       'view_ids': False,
                       'views': False})
        ctx = ast.literal_eval(result['context'])
        invoice_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        ctx.update({'default_ref': invoice.number,
                    'src_unbilled_invoice_id': invoice.id})
        # Get amount from invoice's move line
        inv_line_accounts = invoice.invoice_line.mapped('account_id')
        inv_move_lines = invoice.move_id.mapped('line_id').\
            filtered(lambda l: l.account_id in inv_line_accounts)
        inv_amount = sum(inv_move_lines.mapped('debit')) - \
            sum(inv_move_lines.mapped('credit'))
        # Unbilled
        move_lines = [{
            'account_id': self.move_line_id.account_id.id,  # Unbillied account
            'credit': inv_amount < 0.0 and -inv_amount or 0.0,
            'debit': inv_amount > 0.0 and inv_amount or 0.0,
            'name': invoice.number,
        }]
        # Invoice Lines
        for line in inv_move_lines:
            move_lines.append({'account_id': line.account_id.id,
                               'credit': line.debit,
                               'debit': line.credit,
                               'name': line.name})
        ctx.update({'default_line_id': move_lines})
        # --
        result['context'] = ctx
        return result
