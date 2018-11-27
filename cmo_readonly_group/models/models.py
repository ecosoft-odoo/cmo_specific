# -*- coding: utf-8 -*-
from openerp import models, api
from .common import ReadonlyCommon


class SaleOrder(models.Model, ReadonlyCommon):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class PurchaseOrder(models.Model, ReadonlyCommon):
    _inherit = 'purchase.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountInvoice(models.Model, ReadonlyCommon):
    _inherit = 'account.invoice'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountVoucher(models.Model, ReadonlyCommon):
    _inherit = 'account.voucher'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class HRExpenseExpense(models.Model, ReadonlyCommon):
    _inherit = 'hr.expense.expense'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(HRExpenseExpense, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountMove(models.Model, ReadonlyCommon):
    _inherit = 'account.move'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res


class AccountMoveLine(models.Model, ReadonlyCommon):
    _inherit = 'account.move.line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountMoveLine, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        res = self.set_right_readonly_group(res)
        return res
