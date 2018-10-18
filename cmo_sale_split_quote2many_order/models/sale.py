# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning


class sale_order(models.Model):
    _inherit = 'sale.order'

    order_plan_ids = fields.One2many(
        'sale.order.customer.plan',
        'quote_id',
        string='Order Reference List',
        copy=True,
    )
    use_multi_customer = fields.Boolean(
        string='Use Multiple Customer',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=False,
        help="It indicates that the sale order has been sent.",
    )
    use_merge = fields.Boolean(
        string='Merge Order Line',
        states={'done': [('readonly', True)]},
        default=False,
        help="Merge order line to be single line.",
    )
    amount_untaxed_order_plan = fields.Float(
        string='Amount Untaxed',
        readonly=True,
        related='amount_untaxed',
    )
    customer_amount = fields.Integer(
        string='Customer Amount',
        compute='_compute_customer_amount',
    )
    sale_order_mode = fields.Selection(
        [('change_price', 'As 1 Job (change price)'),
         ('change_quantity', 'As Units (change quantity)')],
        string='Sale Order Mode',
        requied=True,
        states={'done': [('readonly', True)]},
        default='change_price',
    )
    sale_order_ids = fields.One2many(
        'sale.order',
        'quote_id',
        string='Sale Orders',
    )

    @api.depends('customer_amount')
    @api.onchange('order_plan_ids')
    def _compute_customer_amount(self):
        self.customer_amount = len(self.order_plan_ids)

    @api.multi
    def merge_sale_order_line(self, amount_price):
        self.ensure_one()
        order_lines = self.order_line
        description = '%s %s %s %s %s %s' % (
            self.name or '',
            self.date_order or '',
            self.project_related_id.code or '',
            self.project_related_id.name or '',
            self.event_date_description or '',
            self.venue_description or '',
        )
        new_line = order_lines[0].copy({
            'order_lines_group': 'before',
            'sale_layout_custom_group_id': None,
            'section_code': None,
            'product_id': None,
            'price_unit': (amount_price /
                           (1.0 - (order_lines[0].discount / 100.0))),
            'product_uom_qty': 1.0,
            'name': description,
        })
        order_lines.unlink()
        res = new_line.write({'order_id': self.id})
        self._amount_all()
        return res

    @api.multi
    def adjust_price_sale_order_line(self, amount_price):
        self.ensure_one()
        order_line = self.order_plan_ids
        if order_line and self.sale_order_mode:
            if self.sale_order_mode == 'change_quantity':
                for line in self.order_line:
                    new_quantity = amount_price / self.amount_untaxed \
                        if self.amount_price != 0 else amount_price
                    line.write({
                        'product_uom_qty': new_quantity,
                        'purchase_price': 0.0, })
            elif self.sale_order_mode == 'change_price':
                lines = self.order_line[:-1]
                last_line = self.order_line[-1]
                line_amount = 0
                for line in lines:
                    new_price_unit = \
                        line.price_unit * line.product_uom_qty * \
                        round((amount_price / self.amount_untaxed), 2)
                    line_amount += new_price_unit
                    line.write({
                        'price_unit': new_price_unit,
                        'purchase_price': 0.0,
                        'product_uom_qty': 1, })
                last_price_unit = amount_price - line_amount
                last_line.write({
                    'price_unit': last_price_unit,
                    'purchase_price': 0.0,
                    'product_uom_qty': 1, })
        self._amount_all()

    @api.multi
    def validate_sale_order_plan(self):
        self.ensure_one()
        order_plan = self.order_plan_ids
        order_plan_amount = sum(order_plan.mapped('sale_order_amount'))
        order_plan_percent = sum(order_plan.mapped('sale_order_percent'))
        if (self.use_merge is False) and (self.sale_order_mode is False):
            raise Warning(_("Should select sale order mode "
                            "if not use merge sale order line"))
        if order_plan_amount != self.amount_untaxed:
            raise Warning(_("Order plan have amount not equal with Quotation"))
        if order_plan_amount <= 0.0:
            raise Warning(_("Order plan amount must more than zero"))
        if order_plan_percent <= 0.0:
            raise Warning(_("Order plan percent must more than zero"))
        return order_plan

    @api.multi
    def action_validate_before_convert2order(self):
        for order in self:
            if self.use_multi_customer and self.order_plan_ids:
                order_plan = self.validate_sale_order_plan()
                ctx = self._context.copy()
                fiscalyear_id = self.env['account.fiscalyear'].find()
                ctx["fiscalyear_id"] = fiscalyear_id
                for plan in order_plan:
                    new_sale_order = order.copy({
                        'name': self.env['ir.sequence'].
                        with_context(ctx).get('cmo.sale_order') or '/',
                        'order_type': 'sale_order',
                        'quote_id': self.id,
                        'client_order_ref': self.client_order_ref,
                        'partner_id': plan.customer_id.id,
                        'discount_rate': 0.0,
                    })
                    new_sale_order.write({'active': True})
                    if self.use_merge:
                        new_sale_order.merge_sale_order_line(
                            plan.sale_order_amount)
                    else:
                        new_sale_order.adjust_price_sale_order_line(
                            plan.sale_order_amount)
                    plan.write({'order_ref_id': new_sale_order.id})
                order.signal_workflow('convert_to_order')
            else:
                self.action_button_convert_to_order()

    @api.multi
    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders')
        domain = [
            ('quote_id', 'like', self.id),
            ('order_type', '=', 'sale_order'),
        ]
        result = action.read()[0]
        result.update({'domain': domain})
        return result

    @api.multi
    def action_cancel_draft_sale_orders(self):
        self.ensure_one()
        sale_order_ids = self.env['sale.order'].search([
            '&', ('quote_id', 'like', self.id),
            '&', ('order_type', '=', 'sale_order'),
            ('active', '=', True),
        ])
        if sale_order_ids.filtered(lambda r: r.state not in 'draft'):
            raise Warning(_("One of sale orders was confirmed already."))
        for sale_order in sale_order_ids:
            if sale_order.state in ('draft'):
                sale_order.write({
                    'state': 'cancel',
                    'active': False,
                })
        self.write({'state': 'draft'})
        for order_line in self.order_line:
            order_line.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    @api.model
    def _prepare_invoice(self, order, lines):
        invoice_vals = super(sale_order, self)._prepare_invoice(order, lines)
        if order.partner_id:
            invoice_vals['partner_id'] = order.partner_id.id
        return invoice_vals


class SaleOrderCustomerPlan(models.Model):
    _name = 'sale.order.customer.plan'
    _description = 'Sale Customer Plan'

    quote_id = fields.Many2one(
        'sale.order',
        string='Quotation Refer',
        readonly=True,
        index=True,
        ondelete='cascade',
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        index=True,
        domain=[('customer', '=', True), ],
        required=True,
        ondelete='cascade',
    )
    sale_order_percent = fields.Float(
        string='%',
        digits=(16, 10),
    )
    sale_order_amount = fields.Float(
        string='Amount',
        digits=dp.get_precision('Account'),
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        readonly=True,
        help="Gives the sequence of this line \
              when displaying the sale order plan.",
    )
    order_plan_ref = fields.Text(
        string='Order Reference',
    )
    order_ref_id = fields.Many2one(
        'sale.order',
        string='Sale Order Ref.',
        readonly=True,
        copy=False,
    )
    order_ref_state = fields.Selection(
        related='order_ref_id.state',
        string='State',
    )
    order_ref_name = fields.Char(
        related='order_ref_id.name',
        string='Name',
    )

    @api.onchange('sale_order_percent')
    def _onchange_sale_order_percent(self):
        precision = self.env['decimal.precision']
        prec = precision.precision_get('Account')
        subtotal = self.quote_id.amount_untaxed
        self.sale_order_amount = round(self.sale_order_percent / 100.0 *
                                       subtotal or 0.0, prec)

    @api.onchange('sale_order_amount')
    def _onchange_sale_order_amount(self):
        amount_order = self.quote_id.amount_untaxed
        if amount_order != 0:
            new_percent = (self.sale_order_amount / amount_order) * 100 or 0.0
            if round(new_percent, 6) != round(self.sale_order_percent, 10):
                self.sale_order_percent = new_percent
