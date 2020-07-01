# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
    )


class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    analytic_account = fields.Many2one(
        'account.analytic.account',
        string='Project',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
    )


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    account_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
    )
