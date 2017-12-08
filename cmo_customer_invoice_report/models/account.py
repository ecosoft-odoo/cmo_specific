# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Invoice
        if self._context.get('default_type', False) == 'out_invoice' and\
                self._context.get('type', False) == 'out_invoice' and\
                self._context.get('journal_type', False) == 'sale':
            reports = [
                u'Customer/Invoice',
                u'Customer/Invoice(Project)',
            ]
            self.filter_print_report(res, reports)
        # Customer Refund
        elif self._context.get('default_type', False) == 'out_refund' and\
                self._context.get('type', False) == 'out_refund' and\
                self._context.get('journal_type', False) == 'sale_refund':
            reports = [
                u'Customer/Refund',
            ]
            self.filter_print_report(res, reports)
        # Suplier Invoice
        elif self._context.get('default_type', False) == 'in_invoice' and\
                self._context.get('type', False) == 'in_invoice' and\
                self._context.get('journal_type', False) == 'purchase':
            reports = []
            self.filter_print_report(res, reports)
        # Suplier Refund
        elif self._context.get('default_type', False) == 'in_refund' and\
                self._context.get('type', False) == 'in_refund' and\
                self._context.get('journal_type', False) == 'purchase_refund':
            reports = []
            self.filter_print_report(res, reports)
        return res


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Payment
        if self._context.get('type', False) == 'receipt':
            reports = [
                u'Customer/Payment',
            ]
            self.filter_print_report(res, reports)
        # Customer Receipt
        elif self._context.get('type', False) == 'sale' and\
                self._context.get('default_type', False) == 'sale':
            reports = []
            self.filter_print_report(res, reports)
        # Suplier Payment
        elif self._context.get('type', False) == 'payment':
            reports = [
                u'Supplier/Payment(Cheque)',
                u'Payment/Voucher',
            ]
            self.filter_print_report(res, reports)
        # Customer Receipt
        elif self._context.get('type', False) == 'purchase' and\
                self._context.get('default_type', False) == 'purchase':
            reports = []
            self.filter_print_report(res, reports)
        return res
