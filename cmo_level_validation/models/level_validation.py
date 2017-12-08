# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

DOCTYPE_SELECT = [('employee_expense', 'Employee Expense'),
                  ('employee_advance', 'Employee Advance'),
                  ('employee_clearing', 'Employee Clearing'),
                  ('purchase_order', 'Purchase Order'), ]


class LevelValidataion(models.Model):
    _name = 'level.validation'

    level = fields.Integer(
        string='Level',
        required=True,
    )
    limit_amount = fields.Float(
        string='Limit Amount',
        required=True,
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    user_ids = fields.Many2many(
        'res.users',
        'res_user_purchase_level_validation_rel', 'validation_id', 'user_id',
        string='Users',
    )
    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        readonly=True,
        required=True,
        default=lambda self: self._get_default_doctype(),
    )

    @api.model
    def _get_default_doctype(self):
        doctype = self._context.get('doctype')
        if doctype and doctype in dict(DOCTYPE_SELECT):
            return doctype
        else:
            raise ValidationError(_('Your selected doctype is not valid.'))

    _sql_constraints = [
        ('operating_unit_and_level_uniq',
         'UNIQUE(operating_unit_id, level, doctype)',
         'Operating Unit and Level must be unique!'),
    ]
