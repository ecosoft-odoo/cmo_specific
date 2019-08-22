# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    quote_ref_id = fields.Many2one(
        'sale.order',
        string='Quotation Ref.',
        readonly=True,
    )
    quote_ref_number = fields.Char(
        related='quote_ref_id.name',
        string='Quotation Number',
        states={'paid': [('readonly', True)]},
    )
    quote_ref_date = fields.Char(
        string='Quotation Date',
        states={'paid': [('readonly', True)]},
    )
    project_note = fields.Char(
        string='Description',
        states={'paid': [('readonly', True)]},
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        copy=False,
    )
    validate_date = fields.Datetime(
        'Validate On',
        readonly=True,
        copy=False,
    )
    number_preprint = fields.Char(
        required=True
    )
    amount_untaxed_text_en = fields.Char(
        compute='_compute_amount_untaxed_text_en',
        string='Subtotal (EN)',
    )
    amount_untaxed_text_th = fields.Char(
        compute='_compute_amount_untaxed_text_th',
        string='Subtotal (TH)',
    )
    # invoice_line = fields.One2many(
    #     states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
    # )

    @api.multi
    def _compute_amount_untaxed_text_en(self):
        for invoice in self:
            minus = False
            a = 'Baht'
            b = 'Satang'
            if invoice.currency_id.name == 'JYP':
                a = 'Yen'
                b = 'Sen'
            if invoice.currency_id.name == 'GBP':
                a = 'Pound'
                b = 'Penny'
            if invoice.currency_id.name == 'USD':
                a = 'Dollar'
                b = 'Cent'
            if invoice.currency_id.name == 'EUR':
                a = 'Euro'
                b = 'Cent'
            amount_untaxed = invoice.amount_untaxed
            if amount_untaxed < 0:
                minus = True
                amount_untaxed = -amount_untaxed
            amount_text = amount_to_text(
                amount_untaxed, 'en', a).replace(
                    'and Zero Cent', 'Only').replace(
                        'Cent', b).replace('Cents', b)
            final_amount_text = (minus and 'Minus ' +
                                 amount_text or amount_text).lower()
            invoice.amount_untaxed_text_en = \
                final_amount_text[:1].upper() + final_amount_text[1:]

    @api.multi
    def _compute_amount_untaxed_text_th(self):
        for invoice in self:
            minus = False
            amount_untaxed = invoice.amount_untaxed
            if amount_untaxed < 0:
                minus = True
                amount_untaxed = -amount_untaxed
            amount_text = amount_to_text_th(
                amount_untaxed, invoice.currency_id.name)
            invoice.amount_untaxed_text_th = \
                minus and 'ลบ' + amount_text or amount_text

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date=date, period_id=period_id,
            description=description, journal_id=journal_id,
        )
        res.update({
            'quote_ref_id': invoice.quote_ref_id.id,
            'quote_ref_number': invoice.quote_ref_number,
            'quote_ref_date': invoice.quote_ref_date,
        })
        return res

    @api.multi
    def invoice_validate(self):
        # result = super(AccountInvoice, self.sudo()).invoice_validate()
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            invoice.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Datetime.now()})
        return result

    @api.multi
    def write(self, vals):
        for rec in self:
            res = super(AccountInvoice, self).write(vals)
            invoice_lines = self.env['account.invoice.line'].search([
                ('invoice_id', '=', rec.id)])
            asset_ids = self.env['account.asset']
            for line in invoice_lines:
                if line.asset_id:
                    asset = asset_ids.search([
                        ('id', '=', line.asset_id.id)])
                    asset.write({
                        'customer_invoice_number': rec.number,
                    })
            return res

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form',
    #                     toolbar=False, submenu=False):
    #     res = super(AccountInvoice, self).fields_view_get(
    #         view_id, view_type, toolbar=toolbar, submenu=submenu)
    #
    #     # Suplier Invoice
    #     if self._context.get('default_type', False) == 'in_invoice' and\
    #             self._context.get('type', False) == 'in_invoice' and\
    #             self._context.get('journal_type', False) == 'purchase':
    #         root = etree.fromstring(res['arch'])
    #         root.set('create', 'false')
    #         res['arch'] = etree.tostring(root)
    #     return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    state_related_invoice = fields.Selection(
        [('draft', 'Draft'),
         ('proforma', 'Pro-forma'),
         ('proforma2', 'Pro-forma'),
         ('open', 'Open'),
         ('paid', 'Paid'),
         ('cancel', 'Cancelled'),
         ],
        string='Status',
        related='invoice_id.state',
    )

    @api.multi
    def edit_desc(self):
        self.ensure_one()
        return {
            'name': _("Edit Desc."),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'edit.desc',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'edit_field': 'name'},
            'target': 'new',
        }
