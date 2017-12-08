# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseCreateInvoicePlan(models.Model):
    _inherit = 'purchase.create.invoice.plan'

    invoice_mode = fields.Selection(
        default='change_price',
    )
