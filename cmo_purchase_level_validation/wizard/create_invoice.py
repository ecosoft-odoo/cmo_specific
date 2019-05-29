# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseCreateInvoice(models.TransientModel):
    _inherit = 'purchase.create.invoice'

    @api.model
    def view_init(self, fields_list):
        purchase_id = self._context.get('active_id')
        purchase = self.env['purchase.order'].browse(purchase_id)
        purchase._check_extra_permission(type="create invoices")
