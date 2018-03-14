# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    wht_cert_ids = fields.One2many(
        'account.wht.cert',
        'expense_id',
        string='WTH Cert(s)',
        readonly=True,
    )

    @api.multi
    def open_wht_cert(self):
        self.ensure_one()
        if not self.wht_cert_ids:
            raise ValidationError(_('No WHT Cert!'))
        result = {
            'name': _("WHT Cert."),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.wht.cert',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', self.wht_cert_ids.ids)]
        }
        return result
