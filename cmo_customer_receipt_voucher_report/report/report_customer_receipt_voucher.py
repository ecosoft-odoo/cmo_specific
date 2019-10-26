# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from num2words import num2words


class ReportCustomerReceiptVoucher(models.Model):
    _name = 'report.customer.receipt.voucher'
    _auto = False

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
    )
    amount_untaxed = fields.Float(
        string='Amount Untaxed',
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER()
                    OVER(ORDER BY av.id, aml2.analytic_account_id) AS id,
                   av.id AS voucher_id,
                   aml2.analytic_account_id,
                   SUM(aml2.credit-aml2.debit) AS amount_untaxed
            FROM account_voucher_line avl
            INNER JOIN account_voucher av ON avl.voucher_id = av.id
            LEFT JOIN account_move_line aml ON avl.move_line_id = aml.id
            LEFT JOIN (
                SELECT aml.move_id, aml.analytic_account_id, aml.debit,
                       aml.credit
                FROM account_move_line aml
                LEFT JOIN account_account aa ON aml.account_id = aa.id
                WHERE aa.type != 'receivable' AND aa.id NOT IN (
                    SELECT account_collected_id
                    FROM account_tax
                    UNION
                    SELECT account_paid_id
                    FROM account_tax
                )
            ) aml2 ON aml.move_id = aml2.move_id
            WHERE av.type = 'receipt' AND av.state = 'posted'
            GROUP BY av.id, aml2.analytic_account_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))

    @api.multi
    def get_text_total_amount(self):
        total_amount = sum(self.mapped('voucher_id').mapped('amount'))
        return num2words(total_amount, to='currency', lang='th')

    @api.multi
    def get_vat(self):
        voucher_ids = self.mapped('voucher_id')
        move_line_ids = voucher_ids.mapped('line_ids').mapped('move_line_id') \
            .mapped('move_id').mapped('line_id')
        # Get Account of Tax
        self._cr.execute("""
            select account_collected_id from account_tax
            union
            select account_paid_id from account_tax""")
        vat_account_ids = map(lambda l: l[0], self._cr.fetchall())
        vat_move_line_ids = move_line_ids.filtered(
            lambda l: l.account_id.id in vat_account_ids)
        total_credit_vat = sum(vat_move_line_ids.mapped('credit'))
        total_debit_vat = sum(vat_move_line_ids.mapped('debit'))
        return total_credit_vat - total_debit_vat
