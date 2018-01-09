# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import except_orm


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.onchange('filter_refund')
    def _onchange_filter_refund(self):
        active_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(active_id)
        if invoice and invoice.asset_count > 0:
            raise except_orm(
                _('Asset Warning!'),
                _('There are asset(s) related to the origin invoice, '
                  'make sure you handle them correctly.'))
