# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            if rec.code:
                result.append((rec.id, "[%s] %s" % (rec.code, rec.name)))
            else:
                result.append((rec.id, rec.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
