import json
import re
import uuid
import requests
from datetime import date
from odoo import api, fields, models, _
from ..controllers import ird_functions



from odoo.exceptions import UserError, ValidationError

from odoo.addons import decimal_precision as dp
import logging


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    @api.model
    def run_sql_my(self, qry):
        self._cr.execute(qry)
        # _res = self._cr.fetchall()
        # return _res

    @api.depends('company_id')
    def _perform_compute_action(self):
        # if self.partner_id:
        for rec in self:
            if rec.company_id:
                if rec.company_id.ird_integ == True:
                    rec.ird_integ = True
                else:
                    rec.ird_integ = False

    copy_count = fields.Integer(default=0, string='Print Count', help="used for invoice printcount", store=True)
    bill_post = fields.Boolean(string='Sync state',copy=False, track_visibility='always', default=False)
    # reverse_bill_post = 
    bill_data = fields.Char(string='Bill Data', track_visibility='always')
    last_printed = fields.Datetime(string='Last Printed', default=lambda self: fields.datetime.now(),
                                   track_visibility='always')
    # customer_pan = fields.Char(string='PAN',readonly=True)
    ird_integ = fields.Boolean('Connect to IRD', compute='_perform_compute_action')

    @api.model
    def post_invoices_ird(self):
        inv_objs = self.env['account.move'].search(
            [('state', '=', 'posted'), ('move_type', 'in', ('out_invoice', 'out_refund')), ('bill_post', '=', False),('invoice_date','>=',date(2023,7,17))],limit="10")
        if inv_objs:
            for invoice in inv_objs:
                comp_obj = self.env['res.company'].search([('id', '=', invoice.company_id.id)], limit=1)
                if comp_obj.ird_integ:
                    headers = {
                    "Accept": 'application/json',
                    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNjgzOTQ3OGNiYzkxMTY2YzcwZGUzZjU5OGU3YTMwNjI4ZWNhOGZjODVlMmYzNjBhZmQ3MzlmMTdhZWE5YWFiYWFhMjAyZjc2OTFiMTg5M2EiLCJpYXQiOjE2NTgwNjQwNzEuNjQyNzUyLCJuYmYiOjE2NTgwNjQwNzEuNjQyNzU2LCJleHAiOjE2ODk2MDAwNzEuNjM4NDg3LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.eiIDfSMWSIvdIGHP7_m6IBYRdVmnLm6ISiNbDfWy9gsfrCv3MNOGUR4FFOdfCy93_1ZnM1lcPVLEoATui03A8bIxELPekt3udbnA9-upuVA8n2y47sTtWB-TOBESbyVd4DPVxSWnEt44Tf_sWoPoIhQiwTbc0FzPvyTLB0F4PZPH9qBnbSjRnvlAabiRAhBuH7qB1lt76bqDaB9vYsLF2tV8AOQRt-AyOyJPGv8o-NKXV52KxcLAaCqInyn-WdIoaQiouRdkumrcrf-gK5HD5PXPitg-yNRDyT6ZoK6B3r9onbNtUk9WHXX_8Lu3CoLoBWq0tjxlIl5s9PJJx6FRqxpF2ZCWZEnpsZP1E--81G26KR1gvtDi-d-KuLt2ONdsSTKf0MngBN64mltg_lNPce-3MdpkP0TiXBoIB8cZ77a2Y8_kIwN-jOnfiW8i19HC6i3VKhQNYVy9Re7J0pp04C_WKJaY8oOdsyhbgaOsClsWEvihKCsBzcsVp66f4FXclNzyPTrjsFJekPkHzyE5UyTuttV7c1vswnqFbOSW3aIfTtGUGAVmnLoAqCt--BQNP9ufeoBaLmpIt8w5c7t1edbLc9fAZa6EJrcFocnKVZzR1UdACQb_xaBzYJdjbWhLeAj77qGNKgG3cxbV4feUne0czonCJe8EYOQIaPL19pE",
                    }
                    # d2 =  date(2019, 7, 17)
                    # d3 =  date(2020, 7, 16)
                    fy_yr = comp_obj.fy_prefix
                    if invoice.move_type == 'out_invoice':
                        url = 'https://cbapi.ird.gov.np/api/bill'
                        data = {
                            "username": str(comp_obj.ird_user),
                            "password": str(comp_obj.ird_password),
                            "seller_pan": str(invoice.company_id.vat),
                            "buyer_pan": str(invoice.partner_id.vat) if invoice.partner_id.vat else "",
                            "buyer_name": str(invoice.partner_id.name),
                            "fiscal_year": fy_yr,
                            "invoice_number": str(invoice.name),
                            "invoice_date": ird_functions.date_dot_format(invoice.invoice_date),
                            "total_sales": str(invoice.amount_total),
                            "taxable_sales_vat": str(invoice.amount_untaxed),
                            "vat": str(invoice.amount_tax),
                            "excisable_amount": "0",
                            "excise": "0",
                            "taxable_sales_hst": "0",
                            "hst": "0",
                            "amount_for_esf": "0",
                            "esf": "0",
                            "export_sales": "0",
                            "tax_exempted_sales": "0",
                            "isrealtime": True if invoice.invoice_date == date.today() else False,
                            "datetimeclient": str(date.today())
                        }
                        response = requests.post(url, json=data, headers=headers)
                        # raise UserError(str(response.json()))
                        invoice.bill_data = json.dumps(data) + str(response.json())
                        invoice.bill_post = True
                    # elif invoice.move_type == 'out_refund':
                    #     ref_invoice_number=""
                    #     reason_for_return=""
                    #     try:
                    #         ref = invoice.ref.split(",", 1)
                    #         ref_invoice_number = ref[0].split()[2]
                    #         reason_for_return = ref[1].strip()
                    #     except:
                    #         pass
                    #     url = 'https://cbapi.ird.gov.np/api/billreturn'
                    #     data = {
                    #         "username": str(comp_obj.ird_user),
                    #         "password": str(comp_obj.ird_password),
                    #         "seller_pan": str(invoice.company_id.vat),
                    #         "buyer_pan": str(invoice.partner_id.vat) if invoice.partner_id.vat else "0",
                    #         "buyer_name": str(invoice.partner_id.name),
                    #         "fiscal_year": fy_yr,
                    #         "ref_invoice_number": ref_invoice_number,
                    #         "credit_note_number": str(invoice.name),
                    #         "credit_note_date":ird_functions.date_dot_format(invoice.invoice_date),
                    #         "reason_for_return": reason_for_return,
                    #         "total_sales": str(invoice.amount_total),
                    #         "taxable_sales_vat": str(invoice.amount_untaxed),
                    #         "vat": str(invoice.amount_tax),
                    #         "excisable_amount": "0",
                    #         "excise": "0",
                    #         "taxable_sales_hst": "0",
                    #         "hst": "0",
                    #         "amount_for_esf": "0",
                    #         "esf": "0",
                    #         "export_sales": "0",
                    #         "tax_exempted_sales": "0",
                    #         "isrealtime": True,
                    #         "datetimeclient": str(date.today())
                    #     }
                    #     response = requests.post(url, json=data, headers=headers)
                    #     invoice.bill_data = json.dumps(data) + str(response)
                    #     invoice.bill_post = True
                    #     print(response)
                    else:
                        raise UserError(_('Invalid date i.e out of current Fiscal Year.'))
                else:
                    pass
        else:
            print("All bills posted to IRD")

    @api.depends('amount_total')
    def get_amount_in_words(self):
        amount_in_words = self.currency_id.amount_to_text(self.amount_total)
        return amount_in_words


class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    ird_integ = fields.Boolean('Connect to IRD', default=False)
    ird_user = fields.Char('IRD Username')
    ird_password = fields.Char('IRD Password')
    fy_start = fields.Date('Fiscal Year Start')
    fy_end = fields.Date('Fiscal Year End')
    fy_prefix = fields.Char('FY prefix')


class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat')
    def _valid_pan(self):
        if self.vat:
            if ((len(self.vat) == 0 or len(self.vat) == 9) and self.vat[0:].isdigit() == True):
                pass
                # print("ok")
            else:
                # print("Invalid")(self):
                raise ValidationError(_('Invalid Pan Number'))
