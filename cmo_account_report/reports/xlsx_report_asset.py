# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class AssetView(models.Model):
    _name = 'asset.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    line_date = fields.Date(
        string='Asset Line Date',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset ID',
    )
    asset_line_id = fields.Many2one(
        'account.asset.line',
        string='Asset Line ID',
    )
    before_nbv = fields.Float(
        string='Before NetBookValue'
    )
    method_number = fields.Integer(
        string='Percent',
    )
    depreciated_value = fields.Float(
        string='Depreciated Value',
    )
    remaining_value = fields.Float(
        string='Remaining Value',
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        compute='_compute_move_line',
        string='Move Line ID',
    )
    name_asset = fields.Char(
        string='Name Asset Profile',
    )
    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        string='Asset Profile ID',
    )

    @api.multi
    def _compute_move_line(self):
        MoveLine = self.env['account.move.line']
        Period = self.env['account.period']
        for rec in self:
            try:
                period = Period.find(rec.line_date)
            except Exception:
                period = Period
            dom = [('asset_id', '=', rec.asset_id.id),
                   ('account_id.user_type.report_type', '=', 'expense'),
                   ('journal_id.type', '=', 'general'),
                   ('period_id', '=', period.id)]
            rec.move_line_id = MoveLine.search(dom)

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY asset.number, asset.name) AS id,
                asset.id AS asset_id,
                asset_line.id AS asset_line_id,
                asset_line.line_date AS line_date,
                asset_line.depreciated_value AS depreciated_value,
                asset_line.remaining_value AS remaining_value,
                (100/coalesce(asset.method_number, 0.0)) AS method_number,
                (coalesce(asset_line.remaining_value, 0.0) -
                coalesce(asset_line.depreciated_value, 0.0)) AS before_nbv,
                asset_profile.name AS name_asset,
                asset_profile.id AS asset_profile_id
            FROM account_asset asset
            JOIN account_asset_line asset_line
            ON asset.id = asset_line.asset_id
            JOIN account_asset_profile asset_profile
            ON asset.profile_id = asset_profile.id
            WHERE asset_line.type = 'depreciate'
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportAsset(models.TransientModel):
    _name = 'xlsx.report.asset'
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
    company_id = fields.Many2one(
        'res.company',
    )
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
        if self.calendar_period_id:
            dom += [('line_date', '>=', self.calendar_period_id.date_start),
                    ('line_date', '<=', self.calendar_period_id.date_stop)]
        if self.asset_status:
            dom += [('asset_id.state', '=', self.asset_status)]
        if self.asset_code:
            dom += [('asset_id', 'in', self.asset_code.ids)]
        if self.asset_profile:
            dom += [('asset_profile_id', 'in', self.asset_profile.ids)]
        self.results = Result.search(dom)

    @api.onchange('asset_status')
    def _onchange_asset_status(self):
        if self.asset_status:
            return {'domain': {'asset_code': [
                ('state', '=', self.asset_status)]}}
        else:
            return {'domain': {'asset_code': []}}
