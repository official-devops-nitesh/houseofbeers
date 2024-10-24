# -*- coding: utf-8 -*-

from odoo import models, fields


class Invoice(models.Model):
    _inherit = "account.move"

    inv_print_count = fields.Integer(default=0)
