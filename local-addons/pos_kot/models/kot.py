# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosPreparationDisplayOrder(models.Model):
    _inherit = 'pos_preparation_display.order'

    pos_order_session = fields.Char(
        "POS Session",
        compute="_compute_pos_order"
    )

    pos_order_table = fields.Char(
        "Table",
        compute="_compute_pos_order"
    )

    pos_order_customer = fields.Char(
        "Customer",
        compute="_compute_pos_order"
    )

    pos_order_waiter = fields.Char(
        "Waiter",
        compute="_compute_pos_order"
    )

    def _compute_pos_order(self):
        for order in self:
            order.pos_order_session = order.pos_order_id.session_id.name
            order.pos_order_table = order.pos_order_id.table_id.name
            order.pos_order_customer = order.pos_order_id.partner_id.name
            order.pos_order_waiter = order.pos_order_id.waiter_id.name

    def done_orders_stage(self, preparation_display_id):
        preparation_display = self.env['pos_preparation_display.display'].browse(
            preparation_display_id)
        last_stage = preparation_display.stage_ids[-1]

        for order in self:
            p_dis_order_stage_ids = order.order_stage_ids.filtered(
                lambda order_stage: order_stage.preparation_display_id == preparation_display
            )
            current_order_stage = p_dis_order_stage_ids.filtered(
                lambda order_stage:  order_stage.stage_id == last_stage
            )

            if current_order_stage:
                p_dis_order_stage_ids.unlink()
                order.order_stage_ids.create({
                    'preparation_display_id': preparation_display_id,
                    'stage_id': last_stage.id,
                    'order_id': order.id,
                    'done': True
                })
                # if len(order.order_stage_ids.filtered(lambda order_stage: not order_stage.done)) == 0:
                #     order.unlink()

        preparation_display._send_load_orders_message()
