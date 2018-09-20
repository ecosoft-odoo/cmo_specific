# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


# class AssetRepairView(models.Model):
#     _name = 'asset.repair.view'
#     _auto = False
#
#     id = fields.Integer(
#         string='ID',
#         readonly=True,
#     )
#     asset_id = fields.Many2one(
#         'account.asset',
#         string='Account Asset Id',
#         readonly=True,
#     )
#     asset_repair_id = fields.Many2one(
#         'asset.repair.note',
#         string='Asset Repair Id',
#         readonly=True,
#     )
#     purchase_order_id = fields.Many2one(
#         'purchase.order',
#         string='Purchase Order Id',
#         readonly=True,
#     )
#     costcenter_id = fields.Many2one(
#         'res.costcenter',
#         string='Costcenter Id',
#         readonly=True,
#     )
#     responsible_user_id = fields.Many2one(
#         'res.users',
#         string='Responsible User',
#         readonly=True,
#     )
#     section_id = fields.Many2one(
#         'res.section',
#         string='Section id',
#         readonly=True,
#     )
#
#     def _get_sql_view(self):
#         sql_view = """
#             SELECT ROW_NUMBER() OVER(ORDER BY acr.id, ac.id) AS id,
#                 ac.id as asset_id, acr.id as asset_repair_id,
#                 po.id as purchase_order_id, rc.id as costcenter_id,
#                 ac.responsible_user_id, ac.section_id,
#                 CASE WHEN ac.section_id IS NOT NULL THEN
#                 CONCAT('res.section,', ac.section_id)
#                 WHEN ac.project_id IS NOT NULL THEN
#                 CONCAT('res.project,', ac.project_id)
#                 WHEN ac.invest_asset_id IS NOT NULL THEN
#                 CONCAT('res.invest.asset,', ac.invest_asset_id)
#                 WHEN ac.invest_construction_phase_id IS NOT NULL THEN
#                 CONCAT('res.invest.construction.phase,',
#                 ac.invest_construction_phase_id)
#                 ELSE NULL END AS budget
#                 FROM asset_repair_note acr
#                 JOIN account_asset ac ON acr.asset_id = ac.id
#                 JOIN res_costcenter rc ON ac.costcenter_id = rc.id
#                 LEFT JOIN purchase_order po ON acr.purchase_id = po.id
#         """
#         return sql_view
#
#     def init(self, cr):
#         tools.drop_view_if_exists(cr, self._table)
#         cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
#                    % (self._table, self._get_sql_view()))


class XLSXReportAssetRepair(models.TransientModel):
    _name = 'xlsx.report.asset.repair'
    _inherit = 'report.account.common'

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.asset']
        dom = []
        # if self.as_of_date:
        #     dom += [('asset_repair_id.date', '<=', self.as_of_date)]
        self.results = Result.search(dom)
