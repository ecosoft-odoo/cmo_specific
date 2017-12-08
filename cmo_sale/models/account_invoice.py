# -*- coding: utf-8 -*-
from openerp import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    quote_ref_event_date = fields.Char(
        related='quote_ref_id.event_date_description',
        string='Event Date',
        readonly=True,
    )
    quote_ref_venue = fields.Char(
        related='quote_ref_id.venue_description',
        string='Venue',
        readonly=True,
    )
    others_note = fields.Text(
        related='quote_ref_id.payment_term_description',
        string='Other',
        states={'paid': [('readonly', True)]},
    )
