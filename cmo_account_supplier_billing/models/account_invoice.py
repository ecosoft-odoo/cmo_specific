# -*- coding: utf-8 -*-

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


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
    supplier_billing_amount_total = fields.Float(
        string='Total',
        digits=dp.get_precision('Account'),
        compute='_compute_supplier_billing_amount_total')
    
    @api.one
    @api.depends('amount_total')
    def _compute_supplier_billing_amount_total(self):
        if self.type in ['out_refund', 'in_refund']:
            self.supplier_billing_amount_total = self.amount_total * -1
        else:
            self.supplier_billing_amount_total = self.amount_total

