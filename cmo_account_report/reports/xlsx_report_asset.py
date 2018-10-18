# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _
import ast


class AssetView(models.Model):
    _name = 'asset.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    move_date = fields.Date(
        string='Account Move Line Date',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset ID',
    )
    method_number = fields.Integer(
        string='Percent',
    )
    name_asset = fields.Char(
        string='Name Asset Profile',
    )
    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        string='Asset Profile ID',
    )
    depreciation = fields.Float(
        compute='_compute_depreciation',
        string='Depreciation',
    )
    accumulated_cf = fields.Float(
        compute='_compute_accumulated_cf',
        string='Accumulated Depreciation',
    )
    accumulated_bf = fields.Float(
        compute='_compute_accumulated_bf',
        string='Accumulated Depreciation Before',
    )

    @api.multi
    def _compute_depreciation(self):
        action_id = self._context.get('params', {}).get('action', False)
        if action_id:
            action = self.env['ir.actions.act_window'].browse(action_id)
            wizard_id = \
                ast.literal_eval(action.context).get('wizard_id', False)
            wizard = self.env['xlsx.report.asset'].browse(wizard_id)
            if wizard.filter == 'filter_date':
                date_start = wizard.date_start
                date_end = wizard.date_end
            elif wizard.filter == 'filter_period':
                date_start = wizard.period_start_id.date_start
                date_end = wizard.period_end_id.date_stop
            else:
                date_start = wizard.fiscalyear_start_id.date_start
                date_end = wizard.fiscalyear_end_id.date_stop
            self._cr.execute("""
                SELECT asset.id AS id,
                SUM(move_line.debit - move_line.credit)
                AS depreciation FROM account_move_line move_line
                JOIN account_asset asset ON move_line.asset_id = asset.id
                JOIN account_account account ON
                move_line.account_id = account.id
                JOIN account_account_type account_type ON
                account.user_type = account_type.id
                WHERE account_type.name = 'Depreciation'
                AND move_line.date BETWEEN %s AND %s
                GROUP BY asset.id
            """, (date_start, date_end))
            dictall = self._cr.dictfetchall()
            temp = [(x['id'], {'sum': x['depreciation']}) for x in dictall]
            dict_depreciation = dict(temp)
            for rec in self:
                depre = (dict_depreciation.get(
                         rec.asset_id.id, {}).get('sum', False))
                rec.depreciation = depre

    @api.multi
    def _compute_accumulated_cf(self):
        action_id = self._context.get('params', {}).get('action', False)
        if action_id:
            action = self.env['ir.actions.act_window'].browse(action_id)
            wizard_id = \
                ast.literal_eval(action.context).get('wizard_id', False)
            wizard = self.env['xlsx.report.asset'].browse(wizard_id)
            if wizard.filter == 'filter_date':
                date_end = wizard.date_end
            elif wizard.filter == 'filter_period':
                date_end = wizard.period_end_id.date_stop
            else:
                date_end = wizard.fiscalyear_end_id.date_stop
            self._cr.execute("""
                SELECT asset.id AS id,
                SUM(move_line.credit - move_line.debit)
                AS accumulated_cf FROM account_move_line move_line
                JOIN account_asset asset ON move_line.asset_id = asset.id
                JOIN account_account account ON
                move_line.account_id = account.id
                JOIN account_account_type account_type ON
                account.user_type = account_type.id
                WHERE account_type.name = 'Accumulated Depreciation'
                AND move_line.date <= %s
                GROUP BY asset.id
            """, (date_end,))
            dictall = self._cr.dictfetchall()
            temp = [(x['id'], {'sum': x['accumulated_cf']}) for x in dictall]
            dict_accumulated_cf = dict(temp)
            for rec in self:
                accum = (dict_accumulated_cf.get(
                         rec.asset_id.id, {}).get('sum', False))
                rec.accumulated_cf = accum

    @api.multi
    def _compute_accumulated_bf(self):
        action_id = self._context.get('params', {}).get('action', False)
        if action_id:
            action = self.env['ir.actions.act_window'].browse(action_id)
            wizard_id = \
                ast.literal_eval(action.context).get('wizard_id', False)
            wizard = self.env['xlsx.report.asset'].browse(wizard_id)
            if wizard.filter == 'filter_date':
                date_start = wizard.date_start
            elif wizard.filter == 'filter_period':
                date_start = wizard.period_start_id.date_start
            else:
                date_start = wizard.fiscalyear_start_id.date_start
            self._cr.execute("""
                SELECT asset.id AS id,
                asset.purchase_value - SUM(move_line.credit - move_line.debit)
                AS accumulated_bf FROM account_move_line move_line
                JOIN account_asset asset ON move_line.asset_id = asset.id
                JOIN account_account account ON
                move_line.account_id = account.id
                JOIN account_account_type account_type ON
                account.user_type = account_type.id
                WHERE account_type.name = 'Accumulated Depreciation'
                AND move_line.date < %s
                GROUP BY asset.id
            """, (date_start,))
            dictall = self._cr.dictfetchall()
            temp = [(x['id'], {'sum': x['accumulated_bf']}) for x in dictall]
            dict_accumulated_bf = dict(temp)
            for rec in self:
                accum = (dict_accumulated_bf.get(
                         rec.asset_id.id, {}).get('sum', False))
                rec.accumulated_bf = accum

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY asset_profile_id) AS id, * FROM (
                SELECT move_line.date AS move_date,
                    asset_profile.id AS asset_profile_id,
                    asset_profile.name AS name_asset, asset.id AS asset_id,
                    (100/coalesce(asset.method_number, 0.0)) AS method_number
                FROM account_move_line move_line
                JOIN account_asset asset ON move_line.asset_id = asset.id
                JOIN account_account account
                ON move_line.account_id = account.id
                JOIN account_account_type account_type
                ON account.user_type = account_type.id
                JOIN account_asset_profile asset_profile
                ON asset.profile_id = asset_profile.id
                WHERE account_type.name IN
                    ('Depreciation','Accumulated Depreciation')
                GROUP BY asset.id, asset_profile.id, move_line.date
                UNION ALL
                SELECT move_line.date AS move_date, asset_profile.id
                    AS asset_profile_id, asset_profile.name AS name_asset,
                    asset.id AS asset_id, CASE WHEN
                    coalesce(asset.method_number, 0.0) != 0.0
                    THEN (100/coalesce(asset.method_number, 0.0))
                    ELSE asset.method_number END AS method_number
                FROM account_asset asset
                LEFT JOIN account_move_line move_line
                ON move_line.asset_id = asset.id
                LEFT JOIN account_account account
                ON move_line.account_id = account.id
                LEFT JOIN account_account_type account_type
                ON account.user_type = account_type.id
                LEFT JOIN account_asset_profile asset_profile
                ON asset.profile_id = asset_profile.id
                WHERE asset.id NOT IN (
                    SELECT move_line.asset_id FROM account_move_line move_line
                    JOIN account_account account
                    ON move_line.account_id = account.id
                    JOIN account_account_type account_type
                    ON account.user_type = account_type.id
                    WHERE account_type.name IN ('Depreciation',
                        'Accumulated Depreciation') AND
                        move_line.asset_id IS NOT NULL)
                ) AS aml
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportAsset(models.TransientModel):
    _name = 'xlsx.report.asset'
    _inherit = 'report.account.common'

    asset_status = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Running'),
         ('close', 'Close'),
         ('removed', 'Removed')],
        string=' Asset Status'
    )
    asset_code = fields.Many2many(
        'account.asset',
        string='Asset Code',
    )
    asset_profile = fields.Many2many(
        'account.asset.profile',
        string='Asset Profile',
    )
    date_filter = fields.Char(
        compute='_compute_date_filter',
        string='Date Filter',
    )
    results = fields.Many2many(
        'asset.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['asset.view']
        dom = []
        if self.filter == 'filter_date':
            dom += [('move_date', '>=', self.date_start),
                    ('move_date', '<=', self.date_end)]
        if self.filter == 'filter_period':
            dom += [('move_date', '>=', self.period_start_id.date_start),
                    ('move_date', '<=', self.period_end_id.date_stop)]
        if self.asset_status:
            dom += [('asset_id.state', '=', self.asset_status)]
        if self.asset_code:
            dom += [('asset_id', 'in', self.asset_code.ids)]
        if self.asset_profile:
            dom += [('asset_profile_id', 'in', self.asset_profile.ids)]
        result_id = Result.search(dom)
        self._cr.execute("""
            SELECT min(id) AS id, asset_id FROM asset_view
            WHERE id in %s GROUP BY asset_id ORDER BY id
        """ % (str(tuple(map(int, result_id.ids + [0, 0])))))
        dict_result = self._cr.dictfetchall()
        self.results = map(lambda l: l['id'], dict_result)

    @api.multi
    def _compute_date_filter(self):
        if self.filter == 'filter_date':
            date_start = self.date_start
            date_end = self.date_end
        elif self.filter == 'filter_period':
            date_start = self.period_start_id.date_start
            date_end = self.period_end_id.date_stop
        else:
            date_start = self.fiscalyear_start_id.date_start
            date_end = self.fiscalyear_end_id.date_stop
        self.date_filter = _(('ตั้งแต่วันที่ %s ถึง %s') % (date_start, date_end))

    @api.multi
    def action_get_report(self):
        action = self.env.ref(
            'cmo_account_report.action_xlsx_report_asset_form')
        action.write({'context': {'wizard_id': self.id}})
        return super(XLSXReportAsset, self).action_get_report()

    @api.onchange('asset_status')
    def _onchange_asset_status(self):
        if self.asset_status:
            return {'domain': {'asset_code': [
                ('state', '=', self.asset_status)]}}
        else:
            return {'domain': {'asset_code': []}}
