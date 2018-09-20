# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
        'report.pnd.form',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['report.pnd.form']
        dom = []
        if self.income_tax_form:
            dom += [('income_tax_form', '=', self.income_tax_form)]
        if self.calendar_period_id:
            dom += [('wht_period_id', '=', self.calendar_period_id.id)]
        self.results = Result.search(dom)

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
