# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseInvoicePlan(models.Model):
    _inherit = 'purchase.invoice.plan'

    require_prq = fields.Boolean(
        string='Require PRQ',
        default=False,
        copy=False,
    )
