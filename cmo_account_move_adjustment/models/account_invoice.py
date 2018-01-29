# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    adjust_move_id = fields.Many2one(
        'account.move',
        string='Adjustment Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
    )

    @api.multi
    def action_open_adjust_journal(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_journal_line')
        if not action:
            raise ValidationError(_('No Action'))
        res = action.read([])[0]
        res['domain'] = [('id', '=', self.adjust_move_id.id)]
        return res
