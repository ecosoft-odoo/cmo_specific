# -*- coding: utf-8 -*-
from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context.copy()
        if context.get('group_partner_operating_unit', False):
            users = self.env.user
            operating_unit_id = users.default_operating_unit_id.id or False
            users = self.env['res.users'].search(
                [('default_operating_unit_id', '=', operating_unit_id)])
            partner_ids = users.mapped('partner_id.id')
            args = [('id', 'in', partner_ids)] + args
        return super(ResPartner, self).name_search(
            name, args=args, operator=operator, limit=limit
        )
