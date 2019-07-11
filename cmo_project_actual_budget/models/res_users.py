# -*- coding: utf-8 -*-
from openerp import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    search_project_to_date = fields.Date(
        help="Temp store field, used for getting calculated to date bduget",
    )
