# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportOutputTax(models.TransientModel):
    _name = 'xlsx.report.output.tax'
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
    tax = fields.Many2one(
        'account.tax',
        domain=[('type_tax_use', '=', 'sale'),
                ('is_wht', '=', False)],
        string='Tax',
    )
    results = fields.Many2many(
        'account.tax.report',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.tax.report
        """
        self.ensure_one()
        Result = self.env['account.tax.report']
        dom = [('doc_type', '=', 'sale')]
        if self.calendar_period_id:
            dom += [('report_period_id', '=', self.calendar_period_id.id)]
        if self.tax:
            dom += [('tax_id', '=', self.tax.id)]
        self.results = Result.search(dom, order='invoice_date,invoice_number')
