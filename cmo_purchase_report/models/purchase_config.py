# -*- coding: utf-8 -*-

from openerp import models, fields


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    check_billing_regulations = fields.Text(
        string='Check and billing regulations',
        related='company_id.check_billing_regulations',
    )
