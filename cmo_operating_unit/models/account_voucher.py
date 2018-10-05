# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        # If invices are from different OU, warning.
        for rec in self:
            ou = rec.line_ids.mapped('invoice_id').mapped('operating_unit_id')
            if len(ou) > 1:
                raise ValidationError(_('To make payment, all invoices must '
                                        'come from same operating unit.'))
        res = super(AccountVoucher, self).proforma_voucher()
        # Update to use same OU
        for rec in self:
            ou = rec.line_ids.mapped('invoice_id').mapped('operating_unit_id')
            if len(ou) == 1:
                rec.move_id.line_id.write({'operating_unit_id': ou.id})
        return res
