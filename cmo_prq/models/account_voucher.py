# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.model
    def create(self, vals):
        for rec in vals['line_dr_ids']:
            move_id = rec[2].get('move_line_id', False)
            move_line = self.env['account.move.line'].search(
                [('id', '=', move_id)]
            )
            if move_line.invoice.prq_id.state == 'draft':
                raise ValidationError(_(
                    "PRQ Number %s is not yet approved"
                    ) % move_line.invoice.name)
        return super(AccountVoucher, self).create(vals)
