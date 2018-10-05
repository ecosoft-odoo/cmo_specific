# -*- coding: utf-8 -*-
from openerp import models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'id'
