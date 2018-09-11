# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

DOCTYPE_REPORT_MAP = {'purchase': 'purchase.prq.form',
                      'expense': 'expense.prq.form'}


class PrintPRQWizard(models.TransientModel):
    _name = 'print.prq.wizard'

    doctype = fields.Selection([
        ('purchase', 'Purchase Order'),
        ('expense', 'Expense'),
    ],
        string="Doctype",
        readonly=True,
        default=lambda self: self._get_default_doctype(),
    )

    @api.model
    def _get_default_doctype(self):
        active_ids = self._context.get('active_ids')
        purchase_prq = self.env['purchase.prq'].browse(active_ids)
        doctypes = list(set(purchase_prq.mapped('type')))
        if len(doctypes) > 1:
            raise ValidationError(
                _('Not allow selecting document with > 1 Doctypes'))
        return doctypes[0]

    @api.multi
    def action_print_account_invoice(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        try:
            report_name = DOCTYPE_REPORT_MAP.get(self.doctype, False)
        except Exception:
            report_name = False
        if not report_name:
            raise ValidationError(_('No form for for this Doctype'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
