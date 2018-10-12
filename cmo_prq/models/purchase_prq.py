# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchasePRQ(models.Model):
    _name = 'purchase.prq'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(
        string='Number',
        readonly=True,
    )
    type = fields.Selection(
        [('purchase', 'Purchase Order'),
         ('expense', 'Expense')],
        string='Type',
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order Ref',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice Ref',
        readonly=True,
    )
    installment = fields.Integer(
        string='Installment',
        readonly=True,
    )
    prepare_user_id = fields.Many2one(
        'res.users',
        string='Prepared By',
        default=lambda self: self.env.user,
        readonly=True,
        track_visibility='onchange',
    )
    approve_user_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='purchase_id.partner_id',
        string='Supplier',
        readonly=True,
    )
    project_id = fields.Many2one(
        'project.project',
        related='purchase_id.project_id',
        string='Project Name',
        readonly=True,
    )
    order_ref = fields.Many2one(
        'sale.order',
        related='purchase_id.order_ref',
        string='Quotation Number',
        readonly=True,
    )
    date_order = fields.Datetime(
        related='purchase_id.date_order',
        string='Order Date',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approve', 'Approved'),
         ('done', 'Done'),
         ('reject', 'Rejected')],
        default='draft',
        string='Status',
        copy=False,
        readonly=True,
        track_visibility='onchange',
    )
    note = fields.Text(
        string='Note',
    )
    invoice_line_ids = fields.One2many(
        'account.invoice.line',
        related='invoice_id.invoice_line',
        string='Invoice Detailed',
        readonly=True,
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense Ref',
        readonly=True,
    )
    expense_line_ids = fields.One2many(
        'hr.expense.line',
        related='expense_id.line_ids',
        string='Expense Detailed',
        readonly=True,
    )
    date_approve = fields.Date(
        string='Approved Date',
        index=True,
        readonly=True,
        copy=False,
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    amount_po_untaxed = fields.Float(
        related='invoice_id.amount_untaxed',
        store=False,
    )
    amount_po_tax = fields.Float(
        related='invoice_id.amount_tax',
        store=False,
    )
    amount_po_total = fields.Float(
        related='invoice_id.amount_total',
        store=False,
    )
    amount_expense_total = fields.Float(
        related='expense_id.amount',
        store=False,
    )

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_approve(self):
        for rec in self:
            if not rec.date_approve:
                rec.date_approve = fields.Date.context_today(self)
        self.write({'state': 'approve', 'approve_user_id': self.env.user.id})
        return True

    @api.multi
    def action_reject(self):
        self.write({'state': 'reject'})
        return True

    @api.model
    def create(self, vals):
        # Find doctype_id
        doctype = self.env['res.doctype'].get_doctype('purchase_prq')
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        vals['name'] = self.env['ir.sequence'].next_by_doctype()
        return super(PurchasePRQ, self).create(vals)
