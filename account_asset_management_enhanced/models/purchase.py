# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self)._prepare_inv_line(
            account_id, order_line)
        if not res.get('asset_profile_id') and account_id:
            account = self.env['account.account'].browse(account_id)
            asset_profile = account.asset_profile_id
            if asset_profile:
                res['asset_profile_id'] = asset_profile.id
        return res
