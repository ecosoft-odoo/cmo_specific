# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    check_billing_regulations = fields.Text(
        string='Check and billing regulations',
    )

    @api.model
    def get_default_check_billing_regulations(self, fields):
        cbr = self.env.user.company_id.check_billing_regulations
        return {'check_billing_regulations': cbr}

    @api.multi
    def set_default_check_billing_regulations(self):
        company = self.env.user.company_id
        company.write({
            'check_billing_regulations': self.check_billing_regulations})
