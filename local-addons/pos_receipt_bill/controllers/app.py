from odoo.http import request
from odoo import http


class PosOrderControler(http.Controller):
    @http.route(['/api/pos/pos-order'], type='json', auth="user", methods=['GET', 'POST'], cors='*', csrf=False)
    def get_pos_order(self, **kw):
        order_number = kw['ordernumber']
        pos_order = request.env['pos.order'].sudo().search([
            ('pos_reference', '=', order_number)
        ], limit=1)
        if pos_order:
            return {
                'inv': pos_order.account_move.name if pos_order.account_move else "",
                'count': pos_order.account_move.inv_print_count,
                'invoice_date': pos_order.account_move.invoice_date.strftime("%Y-%m-%d") if pos_order.account_move.invoice_date else "",
                "customer": pos_order.partner_id.name if pos_order.partner_id else "",
                "customerPan": pos_order.partner_id.vat if pos_order.partner_id.vat else "",
                "table": pos_order.table_id.name if pos_order.table_id else "",
                "address": pos_order.partner_id.street if pos_order.partner_id else "",
            }

        return {
            'inv': "",
            'count': "",
            'invoice_date':  "",
            "customer": "",
            "customerPan": "",
            "table":  "",
            "address": "",
        }
