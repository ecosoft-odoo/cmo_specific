# -*- coding: utf-8 -*-
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    brand_type_id = fields.Many2one(
        'project.brand.type',  # res.partner.brand.type
        string='Brand type',
    )
    industry_id = fields.Many2one(
        'project.industry',  # res.partner.industry
        string='Industry',
    )
