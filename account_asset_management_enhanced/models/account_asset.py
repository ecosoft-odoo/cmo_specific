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
    value_net_book = fields.Float(
        string='Net Book Value',
        compute='_compute_value_net_book',
        help='calculate from (purchase value - depreciated value)',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        readonly=True,
        default=lambda self:
            self.env['res.users'].operating_unit_default_get(self._uid)
    )

    @api.multi
    def _compute_value_net_book(self):
        for rec in self:
            rec.value_net_book = rec.purchase_value - rec.value_depreciated

    @api.model
    def _get_depreciation_entry_name(self, seq):
        """ change from code to number """
        return (self.number or str(self.id)) + '/' + str(seq)

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

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.code and record.code != '/':
                name = "[%s] %s" % (record.code, record.name)
            else:
                name = record.name
            res.append((record.id, name))
        return res

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
