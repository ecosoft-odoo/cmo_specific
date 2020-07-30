# -*- coding: utf-8 -*-
from openerp import http

# class CmoFmServices(http.Controller):
#     @http.route('/cmo_fm_services/cmo_fm_services/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cmo_fm_services/cmo_fm_services/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cmo_fm_services.listing', {
#             'root': '/cmo_fm_services/cmo_fm_services',
#             'objects': http.request.env['cmo_fm_services.cmo_fm_services'].search([]),
#         })

#     @http.route('/cmo_fm_services/cmo_fm_services/objects/<model("cmo_fm_services.cmo_fm_services"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cmo_fm_services.object', {
#             'object': obj
#         })