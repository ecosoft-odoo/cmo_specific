# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AssetView(models.AbstractModel):
    _name = 'asset.view'
    _inherit = 'account.asset'

    asset_id = fields.Many2one(
        'account.asset',
        string='Asset ID',
    )
    depreciation = fields.Float(
        string='Depreciation',
    )
    accumulated_cf = fields.Float(
        string='Accumulated Depreciation',
    )
    accumulated_bf = fields.Float(
        string='Accumulated Depreciation Before',
    )


class XLSXReportAsset(models.TransientModel):
    _name = 'xlsx.report.asset'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        [('filter_date', 'Dates'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_period',
    )
    asset_status = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Running'),
         ('close', 'Close'),
         ('removed', 'Removed')],
        string=' Asset Status'
    )
    asset_ids = fields.Many2many(
        'account.asset',
        string='Asset Code',
    )
    asset_profile_ids = fields.Many2many(
        'account.asset.profile',
        string='Asset Profile',
    )
    date_filter = fields.Char(
        compute='_compute_date_filter',
        string='Date Filter',
    )
    # Note: report setting
    accum_depre_account_type = fields.Many2one(
        'account.account.type',
        string='Account Type for Accum.Depre.',
        required=True,
        help="Define account type for accumulated depreciation account, "
        "to be used in report query SQL."
    )
    depre_account_type = fields.Many2one(
        'account.account.type',
        string='Account Type for Depre.',
        required=True,
        help="Define account type for depreciation account, "
        "to be used in report query SQL."
    )
    results = fields.Many2many(
        'asset.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        if domain:
            where_dom = ["and %s %s %s " % (x[0], x[1], isinstance(x[2],
                         basestring) and "'%s'" % x[2] or x[2])
                         for x in domain]
        else:
            where_dom = []
        where_str = 'and'.join(where_dom)
        return where_str

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        # Prepare DOM to filter assets
        if self.asset_status:
            dom += [('state', '=', self.asset_status)]
        if self.asset_ids:
            dom += [('id', 'in', tuple(self.asset_ids.ids + [0]))]
        if self.asset_profile_ids:
            dom += [('profile_id', 'in',
                    tuple(self.asset_profile_ids.ids + [0]))]
        # Prepare fixed params
        date_start = False
        date_end = False
        if self.filter == 'filter_date':
            date_start = self.date_start
            date_end = self.date_end
        if self.filter == 'filter_period':
            date_start = self.period_start_id.date_start
            date_end = self.period_end_id.date_stop
        if not date_start or not date_end:
            raise ValidationError(_('Please provide from and to dates.'))
        accum_depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.accum_depre_account_type.id)]).ids
        depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.depre_account_type.id)]).ids
        where_str = self._domain_to_where_str(dom)
        self._cr.execute("""
            select a.*, id asset_id,
                -- depreciation
                (select coalesce(sum(debit-credit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- depreciation account
                 and ml.date between %s and %s
                 and asset_id = a.id) depreciation,
                -- accumulated_cf
                (select coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulated account
                 and ml.date <= %s -- date end
                 and asset_id = a.id) accumulated_cf,
                -- accumulated_bf
                (select coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulatedp account
                 and ml.date <= %s -- date start
                 and asset_id = a.id) accumulated_bf
            from
            account_asset a where 1=1
        """ + where_str + "order by profile_id",
                         (tuple(depre_account_ids), date_start, date_end,
                          tuple(accum_depre_account_ids), date_end,
                          tuple(accum_depre_account_ids), date_start))
        asset_results = self._cr.dictfetchall()
        ReportLine = self.env['asset.view']
        for line in asset_results:
            self.results += ReportLine.new(line)

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
        self.date_filter = _(
            ('ตั้งแต่วันที่ %s ถึง %s') % (date_start, date_end))

    # @api.multi
    # def action_get_report(self):
    #     action = self.env.ref(
    #         'cmo_account_report.action_xlsx_report_asset_form')
    #     action.sudo().write({'context': {'wizard_id': self.id}})
    #     return super(XLSXReportAsset, self).action_get_report()

    @api.onchange('asset_status')
    def _onchange_asset_status(self):
        if self.asset_status:
            return {'domain': {'asset_ids': [
                ('state', '=', self.asset_status)]}}
        else:
            return {'domain': {'asset_ids': []}}
