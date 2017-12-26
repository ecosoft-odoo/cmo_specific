# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountAssetProfile(models.Model):
    _inherit = 'account.asset.profile'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
    )
    prefix = fields.Char(
        string='Number',
        required=True,
    )

    @api.model
    def _create_sequence_asset(self, prefix):
        name = 'Asset-%s' % (prefix, )
        seq_vals = {'name': name,
                    'prefix': prefix + '-',
                    'padding': 4,
                    'implementation': 'no_gap'}
        new_sequence = self.env['ir.sequence'].create(seq_vals)
        return new_sequence

    @api.model
    def create(self, vals):
        prefix = vals.get('prefix')
        if prefix:
            sequence_id = self.env['ir.sequence'].search([
                ('prefix', '=', prefix + '-'),
            ])
            if sequence_id:
                vals['sequence_id'] = sequence_id[0].id
            else:
                new_sequence = self._create_sequence_asset(prefix)
                vals['sequence_id'] = new_sequence.id
        res = super(AccountAssetProfile, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountAssetProfile, self).write(vals)
        prefix = vals.get('prefix')
        for profile in self:
            if prefix:
                sequence_id = self.env['ir.sequence'].search([
                    ('prefix', '=', prefix + '-'),
                ])
                if sequence_id:
                    profile.write({'sequence_id': sequence_id[0].id})
                else:
                    new_sequence = profile._create_sequence_asset(prefix)
                    profile.write({'sequence_id': new_sequence.id})
        return res
