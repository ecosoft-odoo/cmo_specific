# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


def filter_print_report(res, reports, res_model=[]):
    action = []
    if res.get('toolbar', False) and \
            res.get('toolbar').get('print', False):
        for act in res.get('toolbar').get('print'):
            if act.get('report_name') in reports:
                action.append(act)
            if act.get('res_model') in res_model:
                action.append(act)
        res['toolbar']['print'] = action
    return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

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
                u'cmo.customer.invoice.en',
                u'cmo.customer.invoice.th',
                u'cmo.customer.invoice2.en',
                u'cmo.customer.invoice2.th',
                u'cmo.sale.daybook',
                # u'cmo.receipt.tax.invoice.peo.en',
                # u'cmo.receipt.tax.invoice.peo.th',
                u'cmo.receipt.en',
                u'cmo.receipt.th',
            ]
            filter_print_report(res, reports)
        # Customer Refund
        elif self._context.get('default_type', False) == 'out_refund' and\
                self._context.get('type', False) == 'out_refund' and\
                self._context.get('journal_type', False) == 'sale_refund':
            reports = [
                u'cmo.customer.refund',
                u'cmo.customer.refund.cr.tax',
                u'cmo.sale.daybook',
            ]
            filter_print_report(res, reports)
        # Suplier Invoice
        elif self._context.get('default_type', False) == 'in_invoice' and\
                self._context.get('type', False) == 'in_invoice' and\
                self._context.get('journal_type', False) == 'purchase':
            reports = [
                u'cmo.purchase.daybook',
            ]
            filter_print_report(res, reports)
        # Suplier Refund
        elif self._context.get('default_type', False) == 'in_refund' and\
                self._context.get('type', False) == 'in_refund' and\
                self._context.get('journal_type', False) == 'purchase_refund':
            reports = [
                u'cmo.purchase.daybook',
            ]
            filter_print_report(res, reports)
        return res


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    # Receipt/Tax Invoice (PEO)
    invoice_line_ids = fields.Many2many(
        comodel_name='account.invoice.line',
        compute='_compute_report_data',
    )
    invoice_comment = fields.Char(
        compute='_compute_report_data',
    )
    invoice_number_preprint = fields.Char(
        compute='_compute_report_data',
    )
    invoice_amount_untaxed = fields.Float(
        compute='_compute_report_data',
    )
    invoice_amount_tax = fields.Float(
        compute='_compute_report_data',
    )
    invoice_amount_total = fields.Float(
        compute='_compute_report_data',
    )
    invoice_amount_total_text_en = fields.Char(
        compute='_compute_report_data',
    )
    invoice_amount_total_text_th = fields.Char(
        compute='_compute_report_data',
    )

    @api.multi
    def _get_invoice_amount_total_text_en(self, amount_total):
        self.ensure_one()
        minus = False
        a, b = 'Baht', 'Satang'
        if self.currency_id.name == 'JYP':
            a, b = 'Yen', 'Sen'
        if self.currency_id.name == 'GBP':
            a, b = 'Pound', 'Penny'
        if self.currency_id.name == 'USD':
            a, b = 'Dollar', 'Cent'
        if self.currency_id.name == 'EUR':
            a, b = 'Euro', 'Cent'
        if amount_total < 0:
            minus = True
            amount_total = -amount_total
        amount_text = amount_to_text(
            amount_total, 'en', a).replace(
                'and Zero Cent', 'Only').replace(
                    'Cent', b).replace('Cents', b)
        final_amount_text = (minus and 'Minus ' +
                             amount_text or amount_text).lower()
        return final_amount_text[:1].upper() + final_amount_text[1:]

    @api.multi
    def _get_invoice_amount_total_text_th(self, amount_total):
        minus = False
        if amount_total < 0:
            minus = True
            amount_total = -amount_total
        amount_text = amount_to_text_th(amount_total, self.currency_id.name)
        final_amount_text = minus and 'ลบ' + amount_text or amount_text
        return final_amount_text

    @api.multi
    def _compute_report_data(self):
        for rec in self:
            invoices = rec.line_ids.mapped('move_line_id.invoice')
            rec.invoice_line_ids = invoices.mapped('invoice_line')
            rec.invoice_comment = ', '.join(list(set(filter(
                    lambda x: x, invoices.mapped('comment')))))
            rec.invoice_number_preprint = ', '.join(list(set(filter(
                    lambda x: x and x != '-',
                    invoices.mapped('number_preprint')))))
            amount_untaxed, amount_tax, amount_total = 0.0, 0.0, 0.0
            for invoice in invoices:
                sign = invoice.type == 'out_refund' and (-1) or 1
                amount_untaxed += sign * invoice.amount_untaxed
                amount_tax += sign * invoice.amount_tax
                amount_total += sign * invoice.amount_total
            rec.invoice_amount_untaxed = amount_untaxed
            rec.invoice_amount_tax = amount_tax
            rec.invoice_amount_total = amount_total
            rec.invoice_amount_total_text_en = \
                self._get_invoice_amount_total_text_en(amount_total)
            rec.invoice_amount_total_text_th = \
                self._get_invoice_amount_total_text_th(amount_total)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Payment
        if self._context.get('type', False) == 'receipt':
            reports = [
                u'cmo.customer.payment.en',
                u'cmo.customer.payment.th',
                u'cmo.receipt.voucher',
                u'cmo.customer.payment.receipt.mig',
                u'cmo.customer.payment.receipt.tax.invoice.peo.en',
                u'cmo.customer.payment.receipt.tax.invoice.peo.th',
            ]
            filter_print_report(res, reports)
        # Customer Receipt
        elif self._context.get('type', False) == 'sale' and\
                self._context.get('default_type', False) == 'sale':
            reports = []
            filter_print_report(res, reports)
        # Suplier Payment
        elif self._context.get('type', False) == 'payment':
            reports = [
                # u'cmo.supplier.payment.cheque',
                # u'cmo.supplier.payment.voucher',
            ]
            res_model = [
                u'print.document.wizard',
            ]
            filter_print_report(res, reports, res_model)
        # Customer Receipt
        elif self._context.get('type', False) == 'purchase' and\
                self._context.get('default_type', False) == 'purchase':
            reports = []
            filter_print_report(res, reports)
        return res
