# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class WizAccountAssetReport(models.TransientModel):

    _name = 'wiz.account.asset.report'
    _description = 'Financial Assets report'

    fiscalyear_id = fields.Many2one(
        comodel_name='account.fiscalyear',
        string='Fiscal Year', required=True)
    parent_asset_id = fields.Many2one(
        comodel_name='account.asset',
        string='Asset Filter', domain=[('type', '=', 'view')])
    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    profile_ids = fields.Many2many(
        'account.asset.profile',
        string='Asset Profile',
    )

    @api.multi
    def xls_export(self):
        self.ensure_one()
        asset_obj = self.env['account.asset']
        # profile_asset = self.profile_ids
        # parent_asset = self.parent_asset_id
        # if not parent_asset:
        #     parents = asset_obj.search(
        #         [('type', '=', 'view'), ('parent_id', '=', False)])
        #     if not parents:
        #         raise UserError(
        #             _('Configuration Error'),
        #             _("No top level asset of type 'view' defined!"))
        #     parent_asset = parents[0]

        # sanity check
        errors = asset_obj.search([
            ('type', '=', 'normal'),
            ('profile_id', '=', False),
            ])  # ('parent_id', '=', False)
        for err in errors:
            error_name = err.name
            if err.code:
                error_name += ' (' + err.code + ')' or ''
            raise UserError(
                _('Configuration Error'),
                _("No parent asset defined for asset '%s'!") % error_name)

        # if profile_asset:
        #     domain = [('type', '=', 'normal'),
        #               ('profile_id', 'child_of', profile_asset.ids)]
        #     assets = asset_obj.search(domain)
        #     if not assets:
        #         raise UserError(
        #             _('No Data Available'),
        #             _('No records found for your asset profiles selection!'))

        datas = {
            'model': 'account.asset',
            'fiscalyear_id': self.fiscalyear_id.id,
            # 'ids': parent_asset.ids,  # [parent_asset.id],
            'period_id': self.period_id.id or False,
            'profile_ids': self.profile_ids.ids or False,
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.depreciation.xls',
                'datas': datas}
