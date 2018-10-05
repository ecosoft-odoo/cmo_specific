# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAssetLine(models.Model):
    _inherit = 'account.asset.line'

    @api.model
    def _setup_move_line_data(self, depreciation_date, period,
                              account, type, move_id):
        res = super(AccountAssetLine, self)._setup_move_line_data(
            depreciation_date, period, account, type, move_id)
        asset = self.asset_id
        res['operating_unit_id'] = asset.operating_unit_id.id
        return res
