# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    check_billing_regulations = fields.Text(
        string='Check and billing regulations',
        default=lambda l: l._default_check_billing_regulations(),
    )

    @api.onchange('check_billing_regulations')
    def _onchange_billing_regulations(self):
        company_id = self.env.user.company_id
        company_id.write(
            {'check_billing_regulations': self.check_billing_regulations})

    @api.model
    def _default_check_billing_regulations(self):
        return self.env.user.company_id.check_billing_regulations
