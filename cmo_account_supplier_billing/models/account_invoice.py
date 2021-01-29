# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_billing_partner_id = fields.Many2one(
        'res.partner',
        related='supplier_billing_id.partner_id',
        string='Supplier Billing',
    )
    supplier_billing_date = fields.Date(
        related='supplier_billing_id.date',
        string='Billing Date',
    )
    supplier_billing_due_date = fields.Date(
        related='supplier_billing_id.due_date',
        string='Due Date',
    )

