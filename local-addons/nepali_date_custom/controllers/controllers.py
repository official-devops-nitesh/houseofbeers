# -*- coding: utf-8 -*-
# from odoo import http


# class NepaliDateCustom(http.Controller):
#     @http.route('/nepali_date_custom/nepali_date_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nepali_date_custom/nepali_date_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nepali_date_custom.listing', {
#             'root': '/nepali_date_custom/nepali_date_custom',
#             'objects': http.request.env['nepali_date_custom.nepali_date_custom'].search([]),
#         })

#     @http.route('/nepali_date_custom/nepali_date_custom/objects/<model("nepali_date_custom.nepali_date_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nepali_date_custom.object', {
#             'object': obj
#         })

