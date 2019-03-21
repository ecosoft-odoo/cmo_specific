# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Making sure that, then create actual move for cancel and refund
    # do not create asset
    @api.model
    def _switch_move_dict_dr_cr(self, move_dict):
        move_dict = super(AccountMove, self)._switch_move_dict_dr_cr(move_dict)
        move_lines = []
        for line_dict in move_dict['line_id']:
            line_dict[2].update({
                'asset_profile_id': False,  # No profile, no asset created
            })
            move_lines.append((0, 0, line_dict[2]))
        return move_dict


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals, **kwargs):
        res = super(AccountMoveLine, self).create(vals, **kwargs)
        if vals.get('asset_id') and vals.get('asset_profile_id'):
            res.asset_id.write({
                'operating_unit_id': vals['operating_unit_id'] or False,
                'purchase_move_id': res.move_id.id,
                'purchase_date': res.move_id.date,
            })
        return res

    @api.multi
    def write(self, vals, **kwargs):
        res = super(AccountMoveLine, self).write(vals, **kwargs)
        for aml in self:
            if vals.get('operating_unit_id') and aml.asset_id:
                aml.asset_id.write({
                    'operating_unit_id': vals['operating_unit_id'] or False,
                })
        return res
