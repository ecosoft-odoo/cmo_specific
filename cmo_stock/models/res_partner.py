# -*- coding: utf-8 -*-
from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_domain(self, domain):
        context = self._context.copy()
        if context.get('group_partner_operating_unit', False):
            user = self.env.user
            # Partner of all users
            if user.default_operating_unit_id.access_all_operating_unit is \
               True:
                users = self.env['res.users'].search([])
                partner_ids = users.mapped('partner_id.id')
                domain += [('id', 'in', partner_ids)]
                return domain
            # Partner of ou partner same ou user login
            operating_unit_id = user.default_operating_unit_id.id or False
            users = self.env['res.users'].search(
                [('default_operating_unit_id', '=', operating_unit_id)])
            partner_ids = users.mapped('partner_id.id')
            domain += [('id', 'in', partner_ids)]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return super(ResPartner, self).name_search(
            name, args=self._get_domain(args), operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,
                    limit=None, order=None):
        res = super(ResPartner, self).search_read(
            domain=self._get_domain(domain), fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(ResPartner, self).read_group(
            self._get_domain(domain), fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        return res
