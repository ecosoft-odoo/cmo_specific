# -*- coding: utf-8 -*-
from openerp import models, api


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        """ Hack email, so that, it don't remove partner_ids,
        as result we will get both email and notification """
        partner_ids = vals.get('partner_ids', False)
        if partner_ids:
            vals['partner_ids'] = [(4, pid) for pid in partner_ids]
        return super(MailMail, self).create(vals)
