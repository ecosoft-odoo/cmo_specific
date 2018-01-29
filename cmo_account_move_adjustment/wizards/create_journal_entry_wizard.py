# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CreateJournalEntryWizard(models.TransientModel):
    _name = 'create.journal.entry.wizard'

    journal_id = fields.Many2one(
        'account.journal',
        string='Type of Adjustment',
        required=True,
        default=lambda self: self._get_journal_id(),
    )

    @api.model
    def _get_journal_id(self):
        Journal = self.env['account.journal']
        return Journal.search([('code', '=', 'JV')], limit=1).id

    @api.model
    def view_init(self, fields_list):
        invoice_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.adjust_move_id:
            raise ValidationError(
                _('The adjustmnet journal entry already created!'))

    @api.multi
    def create_journal_entry(self):
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
        ctx.update({
            'default_journal_id': self.journal_id.id,
            'default_operating_unit_id': invoice.operating_unit_id.id,
            'default_ref': invoice.number,
            'src_invoice_id': invoice.id})
        result['context'] = ctx
        return result
