# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchasePrq(models.Model):
    _name = 'purchase.prq'

    name = fields.Char(
        string='Number',
        size=64,
        readonly=True,
        default='',
        copy=False,
    )
    type = fields.Selection(
        [('purchase', 'Purchase'),
         ('expense', 'Expense'),
         ],
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order Ref',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice Ref',
    )
    installment = fields.Integer(
        string='Number of Installment',
        default=0,
        readonly=True,
    )
    prepare_user_id = fields.Many2one(
        'res.users',
        string='Prepared By',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    approve_user_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')],
        string='Status',
        default='draft',
        readonly=True,
    )
    note = fields.Char(
        string='Note',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # invoice_line_ids = fields.One2many(
    #     'account.invoice',
    #     string='Invoice Detailed',
    #     readonly=False,
    #     states={'draft': [('readonly', False)]},
    # )

    @api.multi
    def prq_approve(self):
        for rec in self:
            refer_type = 'purchase'
            doctype = rec.env['res.doctype'].get_doctype(refer_type)
            fiscalyear_id = rec.env['account.fiscalyear'].find()
            rec = rec.with_context(doctype_id=doctype.id,
                                                fiscalyear_id=fiscalyear_id)
            name = rec.env['ir.sequence'].next_by_code('purchase.prq')
            rec.write({'name': name, 'state': 'approved'})

    @api.multi
    def prq_reject(self):
        self.write({'state': 'rejected'})

    @api.multi
    def prq_set_to_draft(self):
        self.write({'state': 'draft'})
