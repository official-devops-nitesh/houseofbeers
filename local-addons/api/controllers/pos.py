import json
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import logging
import time

_logger = logging.getLogger(__name__)


def success_response(message, data):
    headers = [
        ('Content-Type', 'application/json'),
    ]
    return request.make_response(json.dumps({
        'success': True,
        'message': message,
        'data': data
    }), headers)


def failure_response(message, code):
    headers = [(
        'Content-Type', 'application/json'),
    ]
    return request.make_response(
        data=json.dumps({
            'success': False,
            'message': message
        }),
        status=code,
        headers=headers
    )


class PosApis(http.Controller):

    def _check_table_status(self, table_id) -> bool:
        pos_order = request.env['pos.order'].sudo().search([
            ('state', '=', 'draft'),
            ('table_id', '=', table_id)
        ])

        return False if pos_order else True

    def _generate_pos_reference(self, recu=None):
        if recu:
            recu += 1

        # current session
        current_session = request.env['pos.session'].sudo().search([
            ('state', '=', 'opened')
        ], limit=1)
        session_name = current_session.name
        # session name split in 2 parts by /
        session_name_parts = session_name.split("/")
        session_id = session_name_parts[-1][-3:]

        # count current session orders
        orders = request.env['pos.order'].sudo().search_count([
            ('session_id', '=', current_session.id)
        ])

        order = f"0000{recu if recu else '0'}{orders + 1}"[-4:]

        pos_refrence = f"Order 00082-{session_id}-{order}"

        if request.env['pos.order'].sudo().search_count([
            ('pos_reference', '=', pos_refrence)
        ]) > 0:
            if not recu:
                recu = 1
            return self._generate_pos_reference(recu=recu)
        else:
            return pos_refrence

    def _save_to_kithen_display(self, order, orders_lines) -> None:
        display_order = request.env['pos_preparation_display.order'].sudo().create({
            'displayed': True,
            'pos_order_id': order.id,
            'pos_config_id': order.config_id.id,
            'pos_table_id': order.table_id.id,
            'preparation_display_order_line_ids': []
        })

        lines = []
        for orderl in orders_lines:
            old = request.env['pos_preparation_display.orderline'].sudo().create({
                'todo': True,
                'product_id': orderl['product_id'],
                'product_quantity': orderl['qty'],
                'preparation_display_order_id': display_order.id
            })
            lines.append(old.id)

        display_order.preparation_display_order_line_ids = lines

        # list all dispalys
        displays = request.env['pos_preparation_display.display'].sudo().search([
        ])

        for display in displays:
            display._send_load_orders_message()

    @http.route(['/api/waiters'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_employee(self):
        try:
            employees = request.env['hr.employee'].sudo().search([
                ('pin', "!=", None),
                ('active', '=', True),
                ('job_title', 'ilike', 'Waiter')
            ])

            response_employees = []
            for employee in employees:
                response_employees.append({
                    "id": employee.id,
                    "name": employee.name
                })
            return success_response("Waiter Lists", response_employees)
        except Exception as e:
            return failure_response(e.args, 400)

    @http.route(['/api/auth'], type='http', auth="public", methods=['POST'], cors='*', csrf=False)
    def auth(self):
        try:
            request_params = request.httprequest.form
            pin = request_params.get('pin')
            employee_id = request_params.get('employee')

            if not pin:
                raise Exception("Pin cannot be empty")

            if not employee_id:
                raise Exception("Employee cannot be empty")

            employee = request.env['hr.employee'].sudo().search([
                ('id', '=', employee_id)
            ], limit=1)

            if not employee:
                raise Exception("Employee not found")

            if employee.pin == pin:
                response = {
                    "id": employee.id,
                    "name": employee.name,
                    "job_title": employee.job_title,
                    "email": employee.work_email,
                }

                return success_response("Auth Successfully", response)
            else:
                return failure_response("Invalid Pin", 403)

        except Exception as e:
            return failure_response(e.args, 400)

    @http.route(['/api/products'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_product_list(self):
        try:
            products = request.env['product.product'].sudo().search([(
                'available_in_pos', '=', True)
            ])
            products_ret = []
            for p in products:
                products_ret.append({
                    "id": p.id,
                    "name": p.name,
                    "price": p.list_price,
                    "image": ""
                })

            return success_response("Product List", products_ret)
        except Exception as e:
            return failure_response(e.args, 400)

    @http.route(['/api/filter-products'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def search_product_list(self, search=None):
        try:
            if not search:
                raise Exception("Search cannot be empty")
            products = request.env['product.product'].sudo().search([
                ('available_in_pos', '=', True),
                ('name', 'ilike', search)
            ])
            products_ret = []
            for p in products:
                products_ret.append({
                    "id": p.id,
                    "name": p.name,
                    "price": p.list_price,
                    "image": ""
                })

            return success_response("Product List", products_ret)
        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/tables'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_table_list(self):
        try:
            tables = request.env['restaurant.table'].sudo().search([
                ('active', '=', True)
            ])
            tables_ret = []
            for t in tables:
                tables_ret.append({
                    "id": t.id,
                    "name": t.name,
                    "seats": t.seats,
                    "floor": {
                        "id": t.floor_id.id,
                        "name": t.floor_id.name
                    },
                    "is_avaliable": self._check_table_status(t.id)
                })
            return success_response("Table List", tables_ret)
        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/floors'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_floors_list(self):
        try:
            floors = request.env['restaurant.floor'].sudo().search([
                ('active', '=', True)
            ])
            floor_response = []
            for floor in floors:
                tables = []
                for table in floor.table_ids:
                    tables.append({
                        "id": table.id,
                        "name": table.name,
                        "seats": table.seats,
                        "is_avaliable": self._check_table_status(table.id)
                    })
                floor_response.append({
                    "id": floor.id,
                    "name": floor.name,
                    "tables": tables
                })
            return success_response("Floor List", floor_response)
        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/orders'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_orders_list(self):
        try:
            current_session = request.env['pos.session'].sudo().search([
                ('state', '=', 'opened')
            ], limit=1)

            orders = request.env['pos.order'].sudo().search([
                ('session_id', '=', current_session.id),
                ('state', "=", 'draft')
            ])
            orders_response = []
            for order in orders:
                order_lines = []
                for line in order.lines:
                    order_lines.append({
                        "name": line.full_product_name,
                        "qty": f"{line.qty} {line.product_uom_id.name}",
                        "price": line.price_unit,
                        "total": line.price_subtotal_incl
                    })
                orders_response.append({
                    "id": order.id,
                    "name": order.name,
                    "table": {
                        "id": order.table_id.id,
                        "name": order.table_id.name
                    },
                    "guest": order.customer_count,
                    "customer": order.partner_id.name if order.partner_id else "",
                    "amount": order.amount_total,
                    "date": order.date_order.strftime("%Y-%m-%d %H:%M:%S"),
                    "state": order.state,
                    "order_lines": order_lines
                })
            return success_response("Order List", orders_response)
        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/order-history'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_fitlered_orders_list(self, filter_date=None):
        try:
            if filter_date:
                filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            else:
                filter_date = datetime.today()

            one_day_ago = filter_date - timedelta(days=1)

            orders = request.env['pos.order'].sudo().search([
                ('state', 'in', ['paid', 'invoiced', 'done']),
                ('date_order', '>', str(one_day_ago)),
                ('date_order', '<=', str(filter_date))
            ])
            orders_response = []
            for order in orders:
                order_lines = []
                for line in order.lines:
                    order_lines.append({
                        "name": line.full_product_name,
                        "qty": f"{line.qty} {line.product_uom_id.name}",
                        "price": line.price_unit,
                        "total": line.price_subtotal_incl
                    })
                orders_response.append({
                    "id": order.id,
                    "name": order.name,
                    "table": {
                        "id": order.table_id.id,
                        "name": order.table_id.name
                    },
                    "guest": order.customer_count,
                    "customer": order.partner_id.name if order.partner_id else "",
                    "amount": order.amount_total,
                    "date": order.date_order.strftime("%Y-%m-%d %H:%M:%S"),
                    "state": order.state,
                    "order_lines": order_lines
                })

            return success_response("Order History", {
                "total_order": len(orders),
                "date": filter_date.strftime("%Y-%m-%d"),
                "orders": orders_response,
            })

        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/place-order'], type='http', auth="public", methods=['POST'], cors='*', csrf=False)
    def place_order(self, **kwarg):
        try:
            print(kwarg)
            request_params = request.httprequest.form
            print(request_params)
            table_id = request_params.get('table_id')
            employee_id = request_params.get('employee_id')
            order_items = request_params.get('orders')
            guest = request_params.get('guest') or 1
            internal_note = request_params.get("internal_note")
            customer_id = request_params.get("customer_id")

            _logger.info("----------------------")
            _logger.info(employee_id)
            _logger.info("----------------------")

            if not table_id:
                raise Exception("Table Field is Required")

            if not employee_id:
                raise Exception("Employee Field is Required")

            if not order_items:
                raise Exception("Orders Field is Required")

            open_session = request.env['pos.session'].sudo().search([
                ('state', '=', 'opened')
            ], limit=1)

            if not open_session:
                raise Exception("No Opened Session")

            # check if table has order not not
            table_order = request.env["pos.order"].sudo().search([
                ('state', '=', 'draft'),
                ('table_id', '=', int(table_id))
            ], limit=1, order="id desc")

            if table_order:
                table_order.update({
                    "note":  f"{ table_order.note if table_order.note else ''} {internal_note if internal_note else ''}",
                })
                # update order to old item
                orders_lines = []
                total_amount = table_order.amount_total
                total_vat_amount = table_order.amount_tax
                new_products = []
                for item in json.loads(request_params['orders']):
                    product = request.env['product.product'].sudo().search([
                        ('id', '=', item.get('product_id'))
                    ], limit=1)
                    total = product.list_price * int(item.get('qty'))
                    amount_without_vat = total / (1 + (13/100))
                    vat_amount = total - amount_without_vat

                    total_amount += total
                    total_vat_amount += vat_amount
                    new_products.append(product.id)
                    row = {
                        "full_product_name": product.name,
                        "order_id": table_order.id,
                        "product_id": product.id,
                        "price_subtotal": total - vat_amount,
                        "price_subtotal_incl": total,
                        "qty": int(item.get('qty')),
                        "price_unit": product.list_price,
                        "tax_ids_after_fiscal_position":  [1],
                        'tax_ids': [1]
                    }
                    orders_lines.append(row)

                lines_ids = table_order.lines.ids
                for line in orders_lines:
                    ol = request.env['pos.order.line'].sudo().create(line)
                    lines_ids.append(ol.id)

                table_order.write({
                    "amount_tax": total_vat_amount,
                    "amount_total": total_amount,
                    "lines": lines_ids,
                })
                request.env.cr.commit()
                self._save_to_kithen_display(
                    order=table_order,
                    orders_lines=orders_lines
                )

            else:
                # create ne order
                orders_lines = []
                total_amount = 0
                total_vat_amount = 0
                for item in json.loads(request_params['orders']):
                    product = request.env['product.product'].sudo().search([
                        ('id', '=', item.get('product_id'))
                    ], limit=1)
                    total = product.list_price * int(item.get('qty'))
                    amount_without_vat = total / (1 + (13/100))
                    vat_amount = total - amount_without_vat

                    row = {
                        "full_product_name": product.name,
                        "order_id": 1,
                        "product_id": product.id,
                        "price_subtotal": total - vat_amount,
                        "price_subtotal_incl": total,
                        "qty": int(item.get('qty')),
                        "price_unit": product.list_price,
                        "tax_ids_after_fiscal_position": [1],
                        'tax_ids': [1]
                    }

                    total_amount += total
                    total_vat_amount += vat_amount
                    orders_lines.append(row)

                order = request.env['pos.order'].sudo().create({
                    "session_id":  open_session.id,
                    "amount_paid": 0,
                    "amount_return": 0,
                    "amount_tax": total_vat_amount,
                    "amount_total": total_amount,
                    "customer_count": guest,
                    "table_id": table_id,
                    "note": internal_note,
                    "partner_id": customer_id if customer_id else None,
                    "lines": [],
                    "pos_reference": self._generate_pos_reference(),
                    "waiter_id": employee_id,
                    "config_id": open_session.config_id.id,
                    "last_order_preparation_change": {}
                })

                lines_ids = []
                for line in orders_lines:
                    line.update({"order_id": order.id})
                    ol = request.env['pos.order.line'].sudo().create(line)
                    lines_ids.append(ol.id)

                order.lines = lines_ids

                request.env.cr.commit()

                self._save_to_kithen_display(
                    order=order,
                    orders_lines=orders_lines
                )
            return success_response("Order Placed", {})
        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/customers'], type='http', auth="public", methods=['GET'], cors='*', csrf=False)
    def get_customers(self, q=None):
        try:
            if q:
                customers = request.env['res.partner'].sudo().search([
                    "|",
                    ('name', 'ilike', q),
                    ('phone', 'like', q)
                ])
            else:
                customers = request.env['res.partner'].sudo().search([
                    ('customer_rank', '>', 1)
                ], limit=20)

            customer_response = []
            for customer in customers:
                customer_response.append({
                    "id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                })

            return success_response("Customer List", customer_response)
        except Exception as error:
            return failure_response(error.args, 400)

    @http.route(['/api/create-contacts'], type='http', cors="*", auth="public", methods=['POST'], csrf=False)
    def create_contacts(self):
        try:
            request_params = request.httprequest.form
            name = request_params.get('name')
            phone = request_params.get('phone')
            vat = request_params.get('vat')
            email = request_params.get("email")

            if not name:
                raise Exception("Name cannot be empty")

            contact = request.env['res.partner'].sudo().create({
                "name": name,
                "phone": phone,
                "email": email,
                "vat": vat,
            })

            if not contact:
                raise Exception("Fail to create contact")

            response = {
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone,
                "vat": contact.vat,
                "email": contact.email
            }

            return success_response("Customer Created", response)
        except Exception as error:
            return failure_response(error.args, 400)
