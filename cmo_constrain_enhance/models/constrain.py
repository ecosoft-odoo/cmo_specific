# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains('operating_unit_id', 'warehouse_id')
    def _check_wh_operating_unit(self):
        self.ensure_one()
        return True
