# -*- encoding: utf-8 -*-
from openerp import models, fields, api


class AccountReportGeneralLedgerWizard(models.TransientModel):
    _inherit = "general.ledger.webkit"

    operating_unit_ids = fields.Many2many(
        'operating.unit',
        string='Operating Units',
        required=False,
    )
    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Analytic Account',
        required=False,
    )

    @api.multi
    def pre_print_report(self, data):
        data = super(AccountReportGeneralLedgerWizard, self).\
            pre_print_report(data)
        # Pass extra param for OU and Projects
        vals = self.read(['operating_unit_ids', 'analytic_account_ids'])[0]
        if not data.get('extra_params', False):
            data['extra_params'] = {'extra_conditions': {},
                                    'extra_sql_select': False,
                                    'extra_sql_join': False}
        # Condition
        data['extra_params']['extra_conditions'].update({
            'operating_unit_id': vals['operating_unit_ids'],
            'analytic_account_id': vals['analytic_account_ids'], })
        # SQL
        data['extra_params']['extra_sql_select'] = """
            COALESCE(ou.code, '') AS operating_unit,
            COALESCE(aa.code, '') AS analytic,
        """
        data['extra_params']['extra_sql_join'] = """
    LEFT JOIN operating_unit ou on (ou.id = l.operating_unit_id)
    LEFT JOIN account_analytic_account aa on (aa.id = l.analytic_account_id)
        """
        # --
        return data

    @api.multi
    def _print_report(self, data):
        if self._context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(data)
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.cmo_report_general_ledger_xls',
                    'datas': data}
        else:
            return super(AccountReportGeneralLedgerWizard, self).\
                _print_report(data)
