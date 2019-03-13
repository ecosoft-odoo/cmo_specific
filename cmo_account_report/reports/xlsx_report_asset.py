# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AssetView(models.AbstractModel):
    _name = 'asset.view'
    _inherit = 'account.asset'
    _order = 'id'

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
    asset_status_draft = fields.Boolean(
        string='Draft',
    )
    asset_status_open = fields.Boolean(
        string='Running',
    )
    asset_status_close = fields.Boolean(
        string='Close',
    )
    asset_status_removed = fields.Boolean(
        string='Removed',
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
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        where_str = 'and'.join(where_dom)
        return where_str

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        status = []
        # Prepare DOM to filter assets
        if self.asset_status_draft:
            status += ['draft']
        if self.asset_status_open:
            status += ['open']
        if self.asset_status_close:
            status += ['close']
        if self.asset_status_removed:
            status += ['removed']
        if self.asset_ids:
            dom += [('id', 'in', tuple(self.asset_ids.ids + [0]))]
        if self.asset_profile_ids:
            dom += [('profile_id', 'in',
                    tuple(self.asset_profile_ids.ids + [0]))]
        if status:
            dom += [('state', 'in', tuple(status + ['']))]
        # Prepare fixed params
        date_start = False
        date_end = False
        fiscalyear_start = self.fiscalyear_start_id.name
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
        if where_str:
            where_str = 'and ' + where_str
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
                case when SUBSTRING(a.date_start :: text,1,4) >= %s
                then 0 else
                (select a.purchase_value - coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 join account_period ap on ap.id = ml.period_id
                 join account_fiscalyear af on af.id = ap.fiscalyear_id
                 where account_id in %s  -- accumulatedp account
                 and af.name < %s -- fiscalyear start
                 and asset_id = a.id) end accumulated_bf
            from
            account_asset a
            where (a.state != 'close' or a.value_depreciated != 0)
        """ + where_str + "order by profile_id, number",
                         (tuple(depre_account_ids), date_start, date_end,
                          tuple(accum_depre_account_ids), date_end,
                          fiscalyear_start,
                          tuple(accum_depre_account_ids), fiscalyear_start))
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

    @api.multi
    def action_get_report(self):
        action = self.env.ref(
            'cmo_account_report.action_xlsx_report_asset_form')
        action.sudo().write({'context': {'wizard_id': self.id}})
        return super(XLSXReportAsset, self).action_get_report()

    @api.onchange('asset_status')
    def _onchange_asset_status(self):
        if self.asset_status:
            return {'domain': {'asset_ids': [
                ('state', '=', self.asset_status)]}}
        else:
            return {'domain': {'asset_ids': []}}
