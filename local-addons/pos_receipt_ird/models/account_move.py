# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) Avoin.Systems 2020

from odoo import models, fields,api
# noinspection PyProtectedMember
from odoo.tools.translate import _
import re
from datetime import datetime,timedelta
import logging

log = logging.getLogger(__name__)

BARCODE_AMOUNT_LIMIT = 999999.99


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_pos_receipt_filename(self):
        type_string = 'Invoice'
        invoice_numbers = self.name or ''
        if self.move_type in ('in_refund', 'out_refund'):
            type_string = 'Credit_Note'
        filename = '-'.join((
            type_string,
            invoice_numbers,
            self.company_id.display_name,
            self.partner_id.display_name or '')). \
            replace(' ', '-').replace(',', '').replace('--', '-')
        return filename

    @api.model
    def increase_print(self):
        if self.state == "posted":
            self.copy_count +=1

    def get_printedtime(self):
        return (datetime.now() + timedelta(hours=5, minutes=45)).strftime('%m/%d/%Y %H:%M:%S')