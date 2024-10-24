# -*- coding: utf-8 -*-

import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, date, time
import datetime
from odoo.http import request
import re


class IrdReport(models.TransientModel):
    _name = "ird.report"

    from_date = fields.Date('Start Date', required=True, default=date.today())
    to_date = fields.Date('End date', required=True, default=date.today())

    def print_ird_report(self):
        """Redirects to the report with the values obtained from the wizard
        'data['form']': name of employee and the date duration"""
        data = {
            'start_date': self.from_date,
            'end_date': self.to_date,
        }
        return self.env.ref('ird_report.action_report_print_ird').report_action(self, data=data)

    # @api.multi
    # def check_reports(self):
    #     self.ensure_one()
    #     data = {}
    #     data['ids'] = self.env.context.get('active_ids', [])
    #     data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
    #     data['form'] = self.read(['date_from', 'date_to'])[0]
    #     used_context = self._build_contexts(data)
    #     data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
    #     print (data)

    #     return self.env.ref('ird_report.ird_report_template').report_action(self, data=data)

    # invoice_data = fields.Char('Name',)
    # file_name = fields.Binary('Partner Detailed Report', readonly=True)
    # state = fields.Selection([('choose', 'choose'), ('get', 'get')],
    #                          default='choose')
    # journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
    #                                default=lambda self: self.env['account.journal'].search([('type','in',('bank','cash')),('company_id','=',self.env.user.company_id.id)]))
    # # account_ids = fields.Many2many('account.account', 'account_report_daybook_account_rel', 'report_id', 'account_id',
    # #                                'Accounts')
    # partner_id = fields.Many2one('res.partner',string='Partner')
