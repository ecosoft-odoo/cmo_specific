# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class WizPaymentReceiptIntransitReport(models.TransientModel):

    _name = 'wiz.payment.receipt.intransit.report'
    _description = 'Payment Receipt Intransit report'

    posted_date = fields.Date(
            string='Posted Date',
            default=lambda self: fields.Date.context_today(self),
            required=True,
        )
    doc_type = fields.Selection(
        [('payment', 'Payment'),
         ('receipt', 'Receipt'), ],
        string='Type',
        required=True,
    )

    @api.multi
    def xls_export(self):
        self.ensure_one()
        datas = {
            'model': 'account.move.line',
            'posted_date': self.posted_date,
            'doc_type': self.doc_type,
        }
        report_name = '%s.intransit' % str(self.doc_type)
        return {'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': datas}
