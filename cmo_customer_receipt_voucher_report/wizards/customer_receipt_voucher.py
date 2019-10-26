# -*- coding: utf-8 -*-
from openerp import models, fields, api


class CustomerReceiptVoucher(models.TransientModel):
    _name = 'customer.receipt.voucher'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    is_cheque = fields.Boolean(
        string='Cheque ?',
    )
    number_cheque = fields.Char(
        string='Cheque No.',
    )

    @api.multi
    def action_get_report(self):
        self.ensure_one()
        # Get Result Report
        Result = self.env['report.customer.receipt.voucher']
        dom = [('voucher_id.number_cheque', '=', self.number_cheque)]
        if self.partner_id:
            dom += [('voucher_id.partner_id', '=', self.partner_id.id)]
        result = Result.search(dom)
        # Get PDF Report
        report_name = \
            'cmo_customer_receipt_voucher_report.customer_receipt_voucher_pdf'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': {'ids': result.ids, 'model': result._name, },
        }
