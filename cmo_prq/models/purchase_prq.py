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
        readonly=True,
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
        store=True,
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        related='purchase_id.operating_unit_id',
        string='Operating Unit',
        readonly=True,
        store=True,
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
    date_approve = fields.Datetime(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        readonly=True,
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
    payment_by = fields.Selection(
        selection=lambda self: self._get_payment_by_selection(),
        string='Payment By',
    )
    bank_transfer_ref = fields.Text(
        string='Bank Transfer Ref.',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    ac_payee_ref = fields.Text(
        string='A/C Payee Ref.',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    cheque_date = fields.Date(
        string='Cheque Date',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    cheque_received_date = fields.Date(
        string='Cheque Received Date',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    has_wht_amount = fields.Float(
        string='WHT amount',
        compute='_compute_cal_wht',
    )

    @api.multi
    def _compute_cal_wht(self):
        self._cr.execute(
            """
                select prq.id,
                    sum(ail.price_unit * ail.quantity * at.amount)
                    as has_wht_amount
                from purchase_prq prq
                join account_invoice_line ail
                    on prq.invoice_id = ail.invoice_id
                join account_invoice_line_tax alt
                    on ail.id = alt.invoice_line_id
                join account_tax at on alt.tax_id = at.id
                where at.is_wht is true and prq.id in %s
                group by prq.id
            """, (tuple(self.ids), ))
        result = self._cr.fetchall()
        for rec in self:
            amount = dict(result).get(rec.id, False)
            rec.has_wht_amount = amount

    @api.model
    def _get_payment_by_selection(self):
        res = [('cash', 'Cash'),
               ('cashier_cheque', 'Cashier Cheque'),
               ('bank_transfer', 'Bank Transfer'),
               ('ac_payee', 'A/C Payee'), ]
        return res

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_approve(self):
        today = fields.Datetime.now()
        return self.write({'state': 'approve',
                           'approve_user_id': self.env.user.id,
                           'date_approve': today})

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
