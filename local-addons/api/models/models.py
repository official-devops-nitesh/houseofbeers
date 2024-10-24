from odoo import models, fields


class PosOrder(models.Model):
    _inherit = "pos.order"

    waiter_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Waiter'
    )
