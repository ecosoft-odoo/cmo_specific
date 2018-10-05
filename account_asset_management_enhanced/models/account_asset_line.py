# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAssetLine(models.Model):
    _inherit = 'account.asset.line'

    @api.multi
    def write(self, vals):
        write_ctx = self._context
        for dl in self:
            depreciation_line_ids = dl.asset_id.depreciation_line_ids
            if len(depreciation_line_ids) == 1 and dl.type == 'create':
                write_ctx = dict(self._context, allow_asset_line_update=True)
        res = super(AccountAssetLine, self).with_context(
            write_ctx)._write(vals)
        return res

    @api.multi
    def _setup_move_data(self, depreciation_date, period):
        self.ensure_one()
        move_data = super(AccountAssetLine, self).\
            _setup_move_data(depreciation_date, period)
        move_data.update({'name': '/',
                          'ref': self.name})
        return move_data
