# -*- coding: utf-8 -*-
from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name = fields.Char(
        readonly=False,
    )
