# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp


class sale_order(models.Model):
    _inherit = 'sale.order'

    discount_type = fields.Selection(
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )
    amount_untaxed = fields.Float(
        compute='_amount_all',
        store=False,
    )
    amount_tax = fields.Float(
        compute='_amount_all',
        store=False,
    )
    amount_total = fields.Float(
        compute='_amount_all',
        store=False,
    )
    amount_discount = fields.Float(
        compute='_amount_all',
        store=False,
    )
    amount_before_discount = fields.Float(
        string='Subtotal Amount',
        readonly=True,
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        track_visibility='always',
    )

    @api.multi
    def calculate_discount(self):
        self.ensure_one()
        discount = 0
        last_line = False
        if self.discount_rate and self.order_line:
            cur = self.pricelist_id.currency_id
            if self.discount_type == 'percent':
                discount = self.discount_rate
                order_lines = self.order_line
            else:
                amount = sum(self.order_line.mapped(
                    lambda r: r.product_uom_qty * r.price_unit)
                )
                total = amount if amount != 0 else 1.0  # prevent /zero
                discount_rate = self.discount_rate
                discount = float_round((discount_rate / total) * 100.0, 16)
                order_lines = self.order_line[:-1]
                last_line = self.order_line[-1]
            discount_line = 0
            for line in order_lines:
                line.write({'discount': discount})
                discount_line += cur.round(
                    line.price_unit * line.product_uom_qty * discount / 100.0)
            if last_line:
                last_discount = (cur.round(discount_rate - discount_line) /
                                 last_line.price_unit * 100.0)
                last_line.write({'discount': last_discount})

    @api.model
    def create(self, vals):
        res = super(sale_order, self).create(vals)
        res.calculate_discount()
        return res

    @api.multi
    def write(self, vals):
        res = super(sale_order, self).write(vals)
        for order in self:
            if ('discount_rate' in vals) and ('order_line' in vals):
                if 'discount_type' not in vals:
                    vals['discount_type'] = order.discount_type
                if 'discount_rate' not in vals:
                    vals['discount_rate'] = order.discount_rate
                vals['sale_order_record'] = order
                order.calculate_discount()
        return res

    @api.multi
    @api.depends('order_line.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            amount_discount = amount_before_discount = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += self._amount_line_tax(line)
                amount_discount += cur.round(
                    line.product_uom_qty * line.price_unit *
                    line.discount / 100
                )
                amount_before_discount += (line.product_uom_qty *
                                           line.price_unit)
            order.amount_untaxed = cur.round(amount_untaxed)
            order.amount_tax = cur.round(amount_tax)
            order.amount_discount = cur.round(amount_discount)
            order.amount_total = amount_untaxed + amount_tax
            order.amount_before_discount = amount_before_discount

    @api.multi
    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate
            else:
                amount = sum(order.order_line.mapped(
                             lambda r: r.product_uom_qty * r.price_unit))
                total = amount if amount != 0 else 1  # prevent devison by zero
                discount = \
                    float_round((order.discount_rate / total) * 100.0, 16)
                order_lines = order.order_line[:-1] if \
                    len(order.order_line) > 0 else order.order_line
                cur = order.pricelist_id.currency_id
                discount_line = 0
                for line in order_lines:
                    discount_line += cur.round(
                        line.price_unit *
                        line.product_uom_qty *
                        discount / 100.0)
                    line.discount = discount
                if len(order.order_line) > 0:
                    last_line = order.order_line[-1]
                    last_line.discount = (cur.round(
                        order.discount_rate - discount_line) /
                        last_line.price_unit) * 100.0
        self._amount_all()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_subtotal_no_disco = fields.Float(
        string='Sub Total',
        compute='_compute_price_subtotal_no_disco',
    )

    @api.multi
    @api.depends('price_unit', 'product_uom_qty')
    def _compute_price_subtotal_no_disco(self):
        for line in self:
            line.price_subtotal_no_disco = \
                line.price_unit * line.product_uom_qty
