# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class WithholdingIncomeTaxView(models.AbstractModel):
    _name = 'withholding.income.tax.view'

    row_number = fields.Integer(
        string='Row Number',
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
    ref = fields.Char(
        string='Reference',
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
    additional_filing = fields.Boolean(
        string='Additional Filing',
        default=False,
        help="If this cert is marked as additional filing, user will manuall "
        "key in rpt_period",
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
        if self.calendar_period_id:  # use rpt_period_id
            dom += [('c.rpt_period_id', '=', self.calendar_period_id.id)]
        where_str = self._domain_to_where_str(dom)
        if where_str:
            where_str = 'and ' + where_str
        # Additional filing
        where_str += ' and coalesce(additional_filing, false) is %s ' % \
            (self.additional_filing and 'true' or 'false')
        group_by = 'group by c.id, rp.id, ct.id, av.number, hr.number \
            order by date_value,number'
        # self.results = Result.search(dom, order='date_value,number')
        self._cr.execute("""
            select row_number() over (order by c.date, c.number) as sequence,
                c.id as id_wht, c.sequence_display as wht_sequence_display,
                c.number, c.date as date_value, c.income_tax_form, c.tax_payer,
                c.rpt_period_id as wht_period_id, c.id as cert_id,
                rp.id as supplier_ids, ct.id as cert_line_ids,
                round(avg(ct.percent)::numeric, 0) as percent,
            case when c.state != 'cancel'
                then sum(ct.base) else 0.0 end as base_total,
            case when c.state != 'cancel'
                then sum(ct.amount) else 0.0 end as tax_total,
            case when c.voucher_id is not null then av.number
                when hr.number is not null then hr.number
                else c.reference end as ref
            from account_wht_cert c
            join res_partner rp on c.supplier_partner_id = rp.id
            left join wht_cert_tax_line ct on ct.cert_id = c.id
            left join account_voucher av on av.id = c.voucher_id
            left join hr_expense_expense hr on hr.id = c.expense_id
            where c.state not in ('draft', 'cancel')
        """ + where_str + group_by)
        withholding_tax = self._cr.dictfetchall()
        ReportLine = self.env['withholding.income.tax.view']
        prev_number = False
        row_number = 0
        for line in withholding_tax:
            # Remove duplicate data
            if prev_number == line.get('number'):
                line['number'] = False
                line['row_number'] = False
                line['supplier_ids'] = False
                line['date_value'] = False
                line['ref'] = False
            else:
                row_number = row_number + 1
                line['row_number'] = row_number
            # Assign row
            self.results += ReportLine.new(line)
            prev_number = line.get('number')

    # As user choose template, auto selection option you needed for csv output
    @api.onchange('specific_template')
    def _onchange_specific_template(self):
        excel_pnd = 'cmo_account_report.xlsx_report_withholding_income_tax'
        if self.specific_template != excel_pnd:
            self.to_csv = True
            # Optional value for CSV file
            self.csv_delimiter = '|'
            self.csv_extension = 'txt'
            self.csv_quote = False
        else:
            self.to_csv = False

    @api.multi
    def action_get_report(self):
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
                    "Income Tax Form and Report Format is different"))
        return super(XLSXReportWithholdingIncomeTax, self).action_get_report()
