# -*- coding: utf-8 -*-
from openerp import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    project_ref_id = fields.Many2one(
        'project.project',
        related='quote_ref_id.project_related_id',
        string='Project',
        store=True,
        readonly=True,
        help="Reference project through sales order reference",
    )
    project_ref_number = fields.Char(
        related='project_ref_id.project_number',
        string='Project Number',
        readonly=True,
    )
    project_ref_name = fields.Char(
        related='project_ref_id.name',
        string='Project Name',
        readonly=True,
    )

    # @api.multi
    # def write(self, vals):
    #     res = super(AccountInvoice, self).write(vals)
    #     if 'state' in vals and vals['state'] != 'draft':
    #         for rec in self:
    #             if rec.project_ref_id:
    #                 for invoice in rec.project_ref_id.out_invoice_ids:
    #                     if invoice.state in ('open', 'paid'):
    #                         rec.project_ref_id.state = 'invoiced'
    #                         break
    #     return res
