# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class WithholdingIncomeTaxView(models.Model):
    _name = 'withholding.income.tax.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    wht_sequence_display = fields.Char(
        string='WHT Sequence Display',
    )
    number = fields.Char(
        string='Number',
    )
    date_value = fields.Date(
        string='Date Value',
    )
    income_tax_form = fields.Char(
        string='Income Tax Form',
    )
    wht_period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    cert_id = fields.Many2one(
        'account.wht.cert',
        string='Cert',
    )
    supplier_ids = fields.Many2one(
        'res.partner',
        string='Supplier ID',
    )
    tax_payer = fields.Char(
        string='Tax Payer',
    )
    percent = fields.Integer(
        string='Percent',
    )
    base_total = fields.Float(
        string='Base Total',
    )
    tax_total = fields.Float(
        string='Tax Total',
    )
    cert_line_ids = fields.Many2one(
        'wht.cert.tax.line',
        string='Cert Line id'
    )
    sequence = fields.Text(
        string='Sequence',
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT LPAD(row_number() over
                (order by c.sequence_display)::char, 5, '0') AS sequence,
                c.id, c.sequence_display AS wht_sequence_display, c.number,
                c.date AS date_value, c.income_tax_form, c.tax_payer,
                c.period_id AS wht_period_id, c.id AS cert_id,
                rp.id AS supplier_ids, ct.id AS cert_line_ids,
                round(avg(ct.percent), 0) AS percent,
            CASE WHEN c.state != 'cancel'
                then sum(ct.base) ELSE 0.0 END AS base_total,
            CASE WHEN c.state != 'cancel'
                then sum(ct.amount) ELSE 0.0 END AS tax_total
            FROM account_wht_cert c
            JOIN res_partner rp ON c.supplier_partner_id = rp.id
            LEFT JOIN wht_cert_tax_line ct ON ct.cert_id = c.id
            WHERE c.state != 'draft'
            GROUP BY c.id, rp.id, ct.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportWithholdingIncomeTax(models.TransientModel):
    _name = 'xlsx.report.withholding.income.tax'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_period',
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
        default=lambda self: self.env['account.period.calendar'].find(),
    )
    income_tax_form = fields.Selection(
        [('pnd3', 'PND3'),
         ('pnd53', 'PND53')],
        string='Income Tax Form',
        required=True,
    )
    specific_template = fields.Selection(
        selection_add=[
            ('cmo_account_report.xlsx_report_withholding_income_tax', 'Excel'),
            ('cmo_account_report.xlsx_report_withholding_income_tax_text',
             'Text'),
        ],
        string='Report Format',
        default='cmo_account_report.xlsx_report_withholding_income_tax',
        required=True,
    )
    results = fields.Many2many(
        'withholding.income.tax.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['withholding.income.tax.view']
        dom = []
        if self.income_tax_form:
            dom += [('income_tax_form', '=', self.income_tax_form)]
        if self.calendar_period_id:
            dom += [('wht_period_id', '=', self.calendar_period_id.id)]
        self.results = Result.search(dom, order='date_value')

    # As user choose template, auto selection option you needed for csv output
    @api.onchange('specific_template')
    def _onchange_specific_template(self):
        if self.specific_template == \
                'cmo_account_report.xlsx_report_withholding_income_tax_text':
            self.to_csv = True
            # Optional value for CSV file
            self.csv_delimiter = '|'
            self.csv_extension = 'txt'
            self.csv_quote = False
        else:
            self.to_csv = False
