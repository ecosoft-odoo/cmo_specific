# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class PrintDocumentWizard(models.TransientModel):
    _name = 'print.document.wizard'

    document_type = fields.Selection(
        [('payment_voucher', 'Payment Voucher'),
         ('bbl', 'BBL Cheque')],
        string='Document Type',
        required=True,
        readonly=False,
    )

    @api.multi
    def print_document(self):
        self.ensure_one()
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        voucher_id = self._context.get('active_id')
        voucher = self.env['account.voucher'].browse(voucher_id)

        if voucher.payment_type in ('transfer', 'cash'):
            raise ValidationError(
                ('The Payment Type is not Cheque and Cheque(cash) will not \
                  allow print Cheque.'))

        if self.document_type == "bbl":
            action = self.env.ref(
                    'cmo_customer_invoice_report.cmo_supplier_payment_cheque')
            result = action.read()[0]
            result = {
                        'type': 'ir.actions.report.xml',
                        'datas': data,
                        'report_name': 'cmo.supplier.payment.cheque',
                        'context': self._context,
            }
            return result
        else:
            action = self.env.ref(
                    'cmo_customer_invoice_report.cmo_supplier_payment_voucher')
            result = action.read()[0]
            result = {
                        'type': 'ir.actions.report.xml',
                        'datas': data,
                        'report_name': 'cmo.supplier.payment.voucher',
                        'context': self._context,
            }
            return result
