# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ProdutCategory(models.Model):
    _inherit = 'product.category'

    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        string='Asset Profile',
    )

    @api.onchange('asset_profile_id')
    def _onchange_asset_profile_id(self):
        account_asset_id = self.asset_profile_id.account_asset_id
        self.property_account_income_categ = account_asset_id
        self.property_account_expense_categ = account_asset_id
        self.property_stock_account_input_categ = account_asset_id
        self.property_stock_account_output_categ = account_asset_id
