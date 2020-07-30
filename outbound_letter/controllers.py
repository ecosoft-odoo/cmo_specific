# -*- coding: utf-8 -*-

from openerp import http

# class OutboundLetter(http.Controller):
#     @http.route('/outbound_letter/outbound_letter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/outbound_letter/outbound_letter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('outbound_letter.listing', {
#             'root': '/outbound_letter/outbound_letter',
#             'objects': http.request.env['outbound_letter.outbound_letter'].search([]),
#         })

#     @http.route('/outbound_letter/outbound_letter/objects/<model("outbound_letter.outbound_letter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('outbound_letter.object', {
#             'object': obj
#         })