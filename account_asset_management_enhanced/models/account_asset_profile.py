# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountAssetProfile(models.Model):
    _inherit = 'account.asset.profile'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
    )

    @api.model
    def _create_sequence_asset(self, account_id):
        name = 'Asset-%s' % (account_id.code, )
        seq_vals = {'name': name,
                    'prefix': account_id.code + '-',
                    'padding': 4,
                    'implementation': 'no_gap'}
        new_sequence = self.env['ir.sequence'].create(seq_vals)
        return new_sequence

    @api.model
    def create(self, vals):
        account_asset_id = vals.get('account_asset_id')
        if account_asset_id:
            account_id = self.env['account.account'].browse(account_asset_id)
            sequence_id = self.env['ir.sequence'].search([
                ('prefix', '=', account_id.code + '-'),
            ])
            if sequence_id and account_id:
                vals['sequence_id'] = sequence_id[0].id
            elif account_id:
                new_sequence = self._create_sequence_asset(account_id)
                vals['sequence_id'] = new_sequence.id
        res = super(AccountAssetProfile, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountAssetProfile, self).write(vals)
        account_asset_id = vals.get('account_asset_id')
        for profile in self:
            if account_asset_id:
                account_id = self.env['account.account'].browse(
                    account_asset_id)
                sequence_id = self.env['ir.sequence'].search([
                    ('prefix', '=', account_id.code + '-'),
                ])
                if sequence_id and account_id:
                    profile.write({'sequence_id': sequence_id[0].id})
                elif account_id:
                    new_sequence = profile._create_sequence_asset(account_id)
                    profile.write({'sequence_id': new_sequence.id})
        return res
