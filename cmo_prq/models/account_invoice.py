# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    prq_id = fields.Many2one(
        'purchase.prq',
        string='PRQ',
    )

    @api.multi
    def invoice_validate(self):
        for rec in self:
            if rec.prq_id:
                if rec.prq_id.state != 'approve':
                    raise ValidationError(_(
                        "PRQ for this invoice is not yet approved"))
        return super(AccountInvoice, self).invoice_validate()
