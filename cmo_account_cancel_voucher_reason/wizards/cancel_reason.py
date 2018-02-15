# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class AccountVoucherCancel(models.TransientModel):

    _inherit = 'account.voucher.cancel'

    @api.one
    def confirm_cancel(self):
        voucher_ids = self._context.get('active_ids')
        assert len(voucher_ids) == 1, "Only 1 voucher ID expected"
        voucher = self.env['account.voucher'].browse(voucher_ids)
        if voucher.type == 'receipt' and voucher.bank_receipt_id and \
           voucher.bank_receipt_id.state != 'cancel':
            raise UserError(_('Error !!'), _(
                'Customer Payment "Cannot UnReconcile. Please cancel all '
                'related Bank Receipts first"'))
        if voucher.type == 'payment' and voucher.bank_payment_id and \
           voucher.bank_payment_id.state != 'cancel':
            raise UserError(_('Error !!'), _(
                'Supplier Payment "Cannot UnReconcile. Please cancel all '
                'related Bank Payment first"'))
        return super(AccountVoucherCancel, self).confirm_cancel()
