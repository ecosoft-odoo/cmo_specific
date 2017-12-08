# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.float_utils import float_round


class SaleCalManageFee(models.TransientModel):
    _name = 'sale.cal.manage.fee'

    percent_rate = fields.Float(
        string="Rate",
        default=lambda r: 12,
    )

    @api.multi
    def calculate_management_fee(self):
        self.ensure_one()
        order_line = self.env['sale.order.line'].browse(
            self._context['order_line_id'])
        quote = self.env['sale.order'].browse(order_line.order_id.id)
        # if order_line.sale_layout_custom_group_id:
        #     fee = float_round(quote._get_amount_by_custom_group(
        #         order_line.sale_layout_custom_group_id) * \
        #         self.percent_rate / 100, 2)
        # else:
        #     fee = float_round(
        #       quote.amount_before_management_fee * self.percent_rate / 100, 2
        #     )
        fee = float_round(
            quote.amount_before_management_fee * self.percent_rate / 100, 2
        )
        order_line.write({'price_unit': fee})
        return {'type': 'ir.actions.act_window_close'}
