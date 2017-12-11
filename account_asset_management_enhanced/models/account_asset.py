# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    number = fields.Char(
        string='Asset Code',
        copy=False,
    )
    purchase_date = fields.Date(
        string='Purchase Date',
        required=False,
        copy=False,
    )
    purchase_move_id = fields.Many2one(
        'account.move',
        string='Purchase Move',
        readonly=True,
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        readonly=True,
        default=lambda self:
            self.env['res.users'].operating_unit_default_get(self._uid)
    )

    @api.multi
    def validate(self):
        for asset in self:
            if not asset.number:
                if asset.profile_id:
                    number = self.env['ir.sequence'].get_id(
                        asset.profile_id.sequence_id.id)
                    asset.write({
                        'number': number,
                    })
                else:
                    raise ValidationError(_('Asset Profile must be selected.'))
        return super(AccountAsset, self).validate()

    # @api.model
    # def create(self, vals):
    #     if vals.get('number', '/') == '/':
    #         if vals.get('profile_id'):
    #             profile_id = self.env['account.asset.profile'].browse(
    #                 vals.get('profile_id'))
    #             vals['number'] = self.env['ir.sequence'].get_id(
    #                 profile_id.sequence_id.id)
    #         else:
    #             raise ValidationError(_('Asset Profile must be selected.'))
    #     res = super(AccountAsset, self).create(vals)
    #     return res
