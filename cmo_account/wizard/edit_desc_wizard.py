# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class EditDesc(models.TransientModel):
    _name = 'edit.desc'

    name = fields.Text(
        string='Description',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditDesc, self).default_get(fields)
        if not self._context.get('edit_field', False):
            raise ValidationError('No edit_field context passed!')
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        res['name'] = rec[self._context['edit_field']]
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        if not self._context.get('edit_field', False):
            raise ValidationError('No edit_field context passed!')
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        rec.write({self._context['edit_field']: self.name})
        return True
