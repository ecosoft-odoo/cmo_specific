# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class WithholdingIncomeTaxView(models.Model):
    _name = 'withholding.income.tax.view'
    _auto = False

    # id = fields.Integer(
    #     string='ID',
    #     readonly=True,
    # )
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
            ('cmo_account_report.xlsx_report_withholding_income_tax_txt_pnd3',
             'Text PND3'),
            ('cmo_account_report.xlsx_report_withholding_income_tax_txt_pnd53',
             'Text PND53'),
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

    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        where_str = 'and'.join(where_dom)
        return where_str

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        if self.income_tax_form:
            dom += [('c.income_tax_form', '=', self.income_tax_form)]
        if self.calendar_period_id:
            dom += [('c.period_id', '=', self.calendar_period_id.id)]
        where_str = self._domain_to_where_str(dom)
        if where_str:
            where_str = 'and ' + where_str
        group_by = 'group by c.id, rp.id, ct.id order by date_value,number'
        # self.results = Result.search(dom, order='date_value,number')
        self._cr.execute("""
            select row_number() over (order by c.date, c.number) as sequence,
                c.id as id_wht, c.sequence_display as wht_sequence_display,
                c.number, c.date as date_value, c.income_tax_form, c.tax_payer,
                c.period_id as wht_period_id, c.id as cert_id,
                rp.id as supplier_ids, ct.id as cert_line_ids,
                round(avg(ct.percent), 0) as percent,
            case when c.state != 'cancel'
                then sum(ct.base) else 0.0 end as base_total,
            case when c.state != 'cancel'
                then sum(ct.amount) else 0.0 end as tax_total
            from account_wht_cert c
            join res_partner rp on c.supplier_partner_id = rp.id
            left join wht_cert_tax_line ct on ct.cert_id = c.id
            where c.state not in ('draft', 'cancel')
        """ + where_str + group_by)
        withholding_tax = self._cr.dictfetchall()
        ReportLine = self.env['withholding.income.tax.view']
        for line in withholding_tax:
            self.results += ReportLine.new(line)

    # As user choose template, auto selection option you needed for csv output
    @api.onchange('specific_template')
    def _onchange_specific_template(self):
        excel_pnd = 'cmo_account_report.xlsx_report_withholding_income_tax'
        text_pnd3 = \
            'cmo_account_report.xlsx_report_withholding_income_tax_txt_pnd3'
        text_pnd53 = \
            'cmo_account_report.xlsx_report_withholding_income_tax_txt_pnd53'
        if self.specific_template != excel_pnd:
            if (self.specific_template == text_pnd3 and
               self.income_tax_form != 'pnd3') or \
               (self.specific_template == text_pnd53 and
               self.income_tax_form != 'pnd53'):
                raise ValidationError(_(
                    "Income Tax Form and Text File is different"))
            self.to_csv = True
            # Optional value for CSV file
            self.csv_delimiter = '|'
            self.csv_extension = 'txt'
            self.csv_quote = False
        else:
            self.to_csv = False
