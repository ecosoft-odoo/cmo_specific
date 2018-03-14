# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.tools.translate import _


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
    project_ref_code = fields.Char(
        related='project_ref_id.code',
        string='Project Code',
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

    @api.multi
    def action_get_invoice_project_data(self):
        for invoice in self:
            inv_project_data = [
                invoice.project_ref_name or '',
                invoice.quote_ref_number and 'Quotation Number: %s / %s'
                % (invoice.quote_ref_number, invoice.quote_ref_date, ) or '',
                invoice.project_ref_code and 'Project No: %s'
                % (invoice.project_ref_code, ) or '',
                invoice.quote_ref_event_date and
                _('วันที่จัดงาน: ') +
                '%s' % (invoice.quote_ref_event_date, ) or '',
                invoice.quote_ref_venue and
                _('สถานที่จัดงาน: ') + '%s' % (invoice.quote_ref_venue, ) or ''
            ]
            invoice.others_note = '\n'.join(inv_project_data)
