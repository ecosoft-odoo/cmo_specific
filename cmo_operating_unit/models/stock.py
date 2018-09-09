# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move, context=None):
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        operating_unit = self.env['stock.picking'].browse(active_id)
        inv_vals = super(StockPicking, self)._get_invoice_vals(
              key, inv_type, journal_id, move, context=context)
        inv_vals.update({
            'operating_unit_id': operating_unit.operating_unit_id.id,
        })
        return inv_vals
