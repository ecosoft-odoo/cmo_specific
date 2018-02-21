# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools import float_compare
from openerp.tools.translate import _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one(
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )
    order_line = fields.One2many(
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project Name',
        ondelete='restrict',
        domain=[
            ('state', 'in', ['validate', 'open', 'ready_billing']),
        ],
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )
    order_ref = fields.Many2one(
        'sale.order',
        string='Quotation Number',
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
        ondelete='restrict',
    )
    event_date_description = fields.Char(
        string='Event Date',
        size=250,
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )
    venue_description = fields.Char(
        string='Venue',
        size=250,
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )
    po_type_id = fields.Many2one(
        'purchase.order.type.config',
        string='PO Type',
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
        required=True,
    )
    po_project = fields.Boolean(
        string='PO Project',
        related='po_type_id.po_project',
    )
    approve_id = fields.Many2one(
        'hr.employee',
        string='PO Approve',
        states={
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
        required=True,
    )
    operating_unit_id = fields.Many2one(
        change_default=True,
        readonly=['state', 'in', ['done', 'confirm', 'approved', 'cancel']],
    )
    requesting_operating_unit_id = fields.Many2one(
        readonly=['state', 'in', ['done', 'confirm', 'approved', 'cancel']],
    )

    @api.onchange('po_type_id')
    def _onchange_po_type_id(self):
        self.project_id = False
        self.order_ref = False
        self.event_date_description = False
        self.venue_description = False
        self.order_line = False
        self.invoice_method = self.po_type_id.invoice_method or False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.order_ref = False
        self.event_date_description = False
        self.venue_description = False
        for line in self.order_line:
            line.group_id = False
            line.product_ref = False

    @api.onchange('order_ref')
    def _onchange_order_id(self):
        self.event_date_description = self.order_ref.event_date_description
        self.venue_description = self.order_ref.venue_description
        for line in self.order_line:
            line.group_id = False
            line.product_ref = False

    @api.model
    def create(self, vals):
        order = super(PurchaseOrder, self).create(vals)
        order._update_analytic_by_project()
        return order

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if self.state not in ['draft', 'approved']:
            self._check_amount_untaxed()
        self._update_analytic_by_project()
        return res

    @api.multi
    def _check_amount_untaxed(self):
        for order in self:
            po_project = order.po_type_id.po_project or False
            remaining_cost = order.project_id.remaining_cost or 0.0
            if po_project and remaining_cost is not False:
                if float_compare(order.amount_untaxed, remaining_cost, 2) > 0:
                    raise ValidationError(
                        _("PO value (%s) over remaining cost (%s), "
                          "please change value." %
                          ('{:,.2f}'.format(order.amount_untaxed),
                           '{:,.2f}'.format(remaining_cost)))
                    )

    @api.multi
    def _update_analytic_by_project(self):
        for rec in self:
            for line in rec.order_line:
                line.account_analytic_id = self.project_id.analytic_account_id


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_ref = fields.Many2one(
        'product.product',
        string='Product Ref',
    )
    date_planned = fields.Date(
        required=False,
    )
    product_ref_custom_group = fields.Char(
        string='Custom Group',
    )
    product_ref_cat_id = fields.Many2one(
        'sale_layout.category',
        string='Section',
    )
    group_id = fields.Many2one(  # no use
        'sale_layout.custom_group',
        string='Custom Group',
    )
    sale_order_line_ref_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line Ref. for Project only',
    )
    custom_group_readonly = fields.Char(
        related='product_ref_custom_group',
        string='Custome Group',
        readonly=True,
    )
    section_readonly = fields.Many2one(
        related='product_ref_cat_id',
        string='Section',
        readonly=True,
    )
    product_ref_readonly = fields.Many2one(
        related='product_ref',
        string='Product Ref.',
        readonly=True,
    )

    @api.onchange('product_ref_custom_group')
    def _onchange_product_ref_custom_group(self):
        if not self.sale_order_line_ref_id:
            self.product_ref_cat_id = False
            self.product_ref = False

    @api.onchange('product_ref_cat_id')
    def _onchange_product_ref_cat_id(self):
        if not self.sale_order_line_ref_id:
            self.product_ref = False

    @api.onchange('sale_order_line_ref_id')
    def _onchange_sale_order_line_ref_id(self):
        self.product_ref_custom_group = \
            self.sale_order_line_ref_id.sale_layout_custom_group
        self.product_ref_cat_id = \
            self.sale_order_line_ref_id.sale_layout_cat_id
        self.product_ref = self.sale_order_line_ref_id.product_id


class PurchaseOrderTypeConfig(models.Model):
    _name = "purchase.order.type.config"

    name = fields.Char(
        string='PO Type',
    )
    category_id = fields.Many2one(
        'product.category',
        string='Internal Category',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    po_project = fields.Boolean(
        string='PO Project',
        default=False,
    )
    invoice_method = fields.Selection(
        [('manual', 'Based on Purchase Order lines'),
         ('order', 'Based on generated draft invoice'),
         ('picking', 'Based on incoming shipments'),
         ('line_percentage', 'Based on line percentage'),
         ('invoice_plan', 'Invoice Plan'), ],
        string='Invoicing Control',
        required=True,
        default='order',
    )
