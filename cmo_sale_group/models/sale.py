# -*- coding: utf-8 -*-
from openerp import models, api
from .common import Common


class SaleOrder(models.Model, Common):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        user = self.env.user
        sale_readonly_group = \
            'base.group_sale_salesman_all_leads_all_ou_readonly'
        if user.has_group(sale_readonly_group):
            res = self.set_right_readonly_group(res)
        return res
