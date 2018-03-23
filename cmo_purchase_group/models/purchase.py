# -*- coding: utf-8 -*-
from openerp import models, api
from .common import Common


class PurchaseOrder(models.Model, Common):
    _inherit = 'purchase.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        user = self.env.user
        manager_readonly_group = \
            'cmo_purchase_group.group_purchase_manager_readonly'
        if user.has_group(manager_readonly_group):
            res = self.set_right_readonly_group(res)
        return res


class PurchaseOrderLine(models.Model, Common):
    _inherit = 'purchase.order.line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseOrderLine, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        user = self.env.user
        manager_readonly_group = \
            'cmo_purchase_group.group_purchase_manager_readonly'
        if user.has_group(manager_readonly_group):
            res = self.set_right_readonly_group(res)
        return res


class PurchaseOrderTypeConfig(models.Model, Common):
    _inherit = 'purchase.order.type.config'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseOrderTypeConfig, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        user = self.env.user
        manager_readonly_group = \
            'cmo_purchase_group.group_purchase_manager_readonly'
        if user.has_group(manager_readonly_group):
            res = self.set_right_readonly_group(res)
        return res
