# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.multi
    def action_asset_cmo_prepare(self):
        # Only valid for a draft asset with only 1 depre line
        assets = self.filtered(lambda l: l.state == 'draft' and
                               len(l.depreciation_line_ids) == 2)
        for asset in assets:
            # 1) Confirm
            asset.validate()
            # 2) Depre
            lines = asset.depreciation_line_ids.filtered(
                lambda l: not l.init_entry and not l.move_check)
            lines.create_move()
            # 3) Compute
            asset.compute_depreciation_board()
