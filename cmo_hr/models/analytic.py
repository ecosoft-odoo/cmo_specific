# -*- coding: utf-8 -*-
from openerp import models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _get_domain(self, domain):
        context = self._context.copy()
        if context.get('is_project_expense_line', False):
            operating_unit_ids = self.env.user.operating_unit_ids.ids
            project = self.env['project.project'].search([
                ('close_project', '=', True),
                ('operating_unit_id', 'in', operating_unit_ids)
            ])
            domain += [('id', 'in', project.mapped('analytic_account_id').ids)]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return super(AccountAnalyticAccount, self).name_search(
            name, args=self._get_domain(args), operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,
                    limit=None, order=None):
        res = super(AccountAnalyticAccount, self).search_read(
            domain=self._get_domain(domain), fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(AccountAnalyticAccount, self).read_group(
            self._get_domain(domain), fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        return res
