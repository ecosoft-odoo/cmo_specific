# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class EditUnitAmount(models.TransientModel):
    _name = 'edit.unit.amount'

    unit_amount = fields.Float(
        string='Unit Price',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditUnitAmount, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        if not rec.expense_id.state == 'validate':
            raise ValidationError(
                _('Only in state "Waiting Validate", amount can be edited'))
        res['unit_amount'] = rec.unit_amount
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        rec.write({'unit_amount': self.unit_amount})
        return True
