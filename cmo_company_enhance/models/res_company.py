# -*- coding: utf-8 -*-
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    partner_th = fields.Char(
        string="Partner (TH)",
    )
    street_th = fields.Char(
        string="Street (TH)",
    )
    street2_th = fields.Char(
        string="Street2 (TH)",
    )
    city_th = fields.Char(
        string="City (TH)",
    )
    state_th = fields.Char(
        string="State (TH)",
    )
    zip_th = fields.Char(
        string="Zip (TH)",
    )
    country_th = fields.Char(
        string="Country (TH)",
    )