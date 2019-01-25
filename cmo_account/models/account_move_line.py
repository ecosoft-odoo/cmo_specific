# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    opej_ref = fields.Char(
        string='OPEJ Ref',
    )
    ref = fields.Char(
        compute='_compute_ref',  # Changed from related field.
        store=True,
        readonly=True,
        help="Note: still preserve related field funciton (can't remove yet)"
    )

    @api.multi
    @api.depends('move_id')
    def _compute_ref(self):
        """ If opej_ref exists, use it otherwise fall back """
        for rec in self:
            rec.ref = rec.opej_ref or rec.move_id.ref
        return True
