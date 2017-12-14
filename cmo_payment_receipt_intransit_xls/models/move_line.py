# -*- coding: utf-8 -*-

from openerp import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _xls_payment_receipt_intransit_fields(self):
        return [
            'date', 'ref', 'name', 'cheque_number', 'amount'
        ]

    @api.model
    def _xls_payment_receipt_intransit_template(self):
        """
        Template updates

        """
        return {}
