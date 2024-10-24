# -*- coding: utf-8 -*-
import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import  timedelta,date,time
import datetime
from odoo.http import request
import re
import logging
_logger = logging.getLogger(__name__)

class PartnerDetailedReporting(models.TransientModel):
    _name = "partner.detailed.reporting"
    
    invoice_data = fields.Char('Name',)
    file_name = fields.Binary('Partner Detailed Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search([('type','in',('bank','cash','general'))]))
    account_ids = fields.Many2many('account.account', string='Report Accounts') #,compute='rep_account'
    partner_id = fields.Many2one('res.partner',string='Partner')
   
    date_from = fields.Date('Start Date',required='True',default=date.today())
    date_to = fields.Date('End date',required='True',default=date.today())

    def rep_account(self):
        for rec in self:
            kls = []
            _logger.info(self.env.company.rep_account_ids)
            for recs in self.env.company.rep_account_ids:
                _logger.info(recs)
                kls.append(recs.id)
            rec.account_ids = kls

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['account_ids'] = 'account_ids' in data['form'] and data['form']['account_ids'] or False
        result['state'] = 'state' in data['form'] and data['form']['state'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['partner_id'] = data['form']['partner_id'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    # # @api.multi
    def check_reports(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'partner_id', 'invoice_data','account_ids'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.env.ref('partner_detail_report.partner_detailed_pdf_report').report_action(self, data=data)

    # @api.multi
    def action_partner_detailed_report(self):
        # mon_name = datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
        # mon_name = mon_name.strftime("%B")
        # tm = datetime.time(23, 59, 59)
        # dt1 = datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
        # dt2 = datetime.datetime.strptime(self.date_to, "%Y-%m-%d").date()
        m_date_from = str(self.date_from)
        m_date_to = str(self.date_to)
        workbook = xlwt.Workbook()
        format0 = xlwt.easyxf('font:height 300, bold True; pattern: pattern solid, fore_colour gray25; align: horiz center')
        format1 = xlwt.easyxf('font:bold True; pattern: pattern solid, fore_colour gray25; align: horiz left')
        format3 = xlwt.easyxf('align: horiz left')
        format4 = format3
        format5 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour tan; align: horiz left')
        format6 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour tan; align: horiz left')

        sheet = workbook.add_sheet("Partner_detailed_report",cell_overwrite_ok=True)
        sheet.col(0).width = int(12*260)
        sheet.col(1).width = int(15*260)    
        sheet.col(2).width = int(15*260)    
        sheet.col(3).width = int(50*260) 
        sheet.col(4).width = int(14*260)   
        sheet.col(5).width = int(14*260)
        sheet.col(6).width = int(14*260)
        sheet.col(7).width = int(12*260)
        sheet.col(8).width = int(15*260)
        sheet.col(9).width = int(12*260)   
        sheet.col(10).width = int(12*260)
        sheet.col(11).width = int(12*260)   
        sheet.write_merge(0, 1, 0, 6, 'Ledger Report for '+ str(self.partner_id.name) +" from " + str(self.date_from) +" to "+ str(self.date_to),format0)
        sheet.write(2, 2, str("Company"), format1)
        sheet.write(2, 3, str(self.env.company.name), format1)

        sheet.write(3, 0, "Date", format1)
        sheet.write(3, 1, "Ref. Number", format1)
        sheet.write(3, 2, "Type", format1)
        sheet.write(3, 3, "Particulars", format1)
        sheet.write(3, 4, "Debit", format1)
        sheet.write(3, 5, "Credit", format1)
        sheet.write(3, 6, "Balance", format1)
        
        ac = []
        for ids in self.account_ids:
            ac.append(ids.id)

        _logger.info(ac)
        _logger.info(tuple(ac))

        
        self._cr.execute("""select am.id,am.invoice_date as ldate, pt.name as product,aml.quantity,aml.price_unit,aml.price_subtotal,am.name as number,am.move_type as type,am.amount_untaxed,am.amount_tax,am.amount_total,am.partner_id from account_move_line aml 
                                left join account_move am on aml.move_id = am.id  left join product_product p on p.id = aml.product_id left join product_template pt on pt.id = p.product_tmpl_id where am.state ='posted' and 
                                am.move_type IN ('out_invoice','in_invoice','in_refund','out_refund') and am.company_id= %s and aml.account_id IN %s and am.invoice_date BETWEEN %s AND %s  and am.partner_id =%s order by am.id""", (self.env.company.id,tuple(ac),m_date_from,m_date_to,self.partner_id.id,))
        result =  self._cr.dictfetchall()

        _logger.info(result)
        cr = self.env.cr
        
        cr1 = self.env.cr
        cr1.execute("""select COALESCE(sum(l.debit - l.credit),0) as opening_bal
                    from account_move_line l
                    join account_move m on l.move_id = m.id
                    join account_account a on l.account_id = a.id
                    where a.internal_type in ('receivable','payable') and m.state = 'posted' and
                    l.company_id = %s and l.partner_id = %s and l.date < %s""" , (self.env.company.id,self.partner_id.id,m_date_from))
        result11 = cr1.dictfetchone()
        _logger.info(result11)
        opening_balance = result11['opening_bal']
        _logger.info(result11)
        # opening_balance += result11['opening_bal']
        sql = ('''
                        SELECT l.id AS lid, acc.name as accname,acc.code as acccode, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, 
                        l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                        COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                        m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name,l.create_uid as cid
                        FROM account_move_line l
                        JOIN account_move m ON (l.move_id=m.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                        JOIN account_account acc ON (l.account_id = acc.id) 
                        WHERE j.type in ('cash','bank','general') AND m.move_type in('entry','out_receipt','in_receipt')
                        AND l.journal_id IN %s AND l.partner_id = %s AND m.state = 'posted' AND l.date BETWEEN %s AND %s
                        GROUP BY l.id, l.account_id, l.date,
                        j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name, acc.code
                        ORDER BY j.code DESC
                ''')
        kl = []
        for ids in self.journal_ids:
            kl.append(ids.id)
        params = (tuple(kl),self.partner_id.id, m_date_from, m_date_to)
        cr.execute(sql, params)
        result_pay = cr.dictfetchall()
        # return data
        # print("================Excel=======================")
        # print(result_pay)
        final_result = result + result_pay
        # print("================Excel=======================")
        # print(result)
        # print(final_result)
        final_result.sort(key=lambda item:item['ldate'])   
        row_number = 5 #4 has opening
        col_number = 0
        tmp =  " "
        # tmp1 = " "
        tmpd = " "
        
        closing_balance = opening_balance
        
        sheet.write(row_number, col_number + 3, "Opening Balance",format4)
        sheet.write(row_number, col_number + 6, str(opening_balance),format4)
        for data in final_result:
            if 'id' in data:
                if data['quantity'] != 0: 
                    if tmp == data['number']:
                        sheet.write(row_number, col_number , " ",
                                format4)
                        sheet.write(row_number, col_number + 1, " ",
                                format4)
                        
                    else:
                        row_number += 1
                        sheet.write(row_number, col_number, str(data['ldate']), format4)
                        sheet.write(row_number, col_number + 1, data['number'],format4)
                        # if data['type'] == 'out_invoice':
                        #     tstr = 'Sales'
                        # elif data['type'] == 'in_invoice':
                        #     tstr = 'Purchase'
                        # elif data['type'] == 'out_refund':
                        #     tstr = 'Sales Return'
                        # elif data['type'] == 'in_refund':
                        #     tstr = 'Purchase Return'
                        # row_number += 1
                        # sheet.write(row_number, col_number+7, str("Account Receivable"), format4)
                        if data['amount_total'] != 0 and data['type'] == 'out_invoice':
                            tstr = 'Sales'
                            closing_balance = (closing_balance + data['amount_total'])
                            sheet.write(row_number, col_number + 4, str(data['amount_total']), format4)
                        elif data['amount_total'] != 0 and data['type'] == 'out_refund':
                            tstr = 'Sales Return'
                            closing_balance = (closing_balance - data['amount_total'])
                            sheet.write(row_number, col_number + 5, str(data['amount_total']), format4)
                        elif data['amount_total'] != 0 and data['type'] == 'in_invoice':
                            tstr = 'Purchase'
                            closing_balance = (closing_balance - data['amount_total'])
                            sheet.write(row_number, col_number + 5, str(data['amount_total']), format4)
                        elif data['amount_total'] != 0 and data['type'] == 'in_refund':
                            tstr = 'Purchase Return'
                            closing_balance = (closing_balance + data['amount_total'])
                            sheet.write(row_number, col_number + 4, str(data['amount_total']), format4)
                        sheet.write(row_number, col_number + 2, tstr,format4)
                        lstr = "Subtotal = " + str("%.2f" % data['amount_untaxed'])+ " // Vat = " +  str("%.2f" % data['amount_tax']) + " // Grand total =" + str("%.2f" % data['amount_total'])
                        sheet.write(row_number, col_number + 3, lstr,format4)
                        # sheet.write(row_number, col_number + 4, str(data['amount_total']), format4)
                        sheet.write(row_number, col_number + 6, str("%.2f" % closing_balance), format4)
                        row_number +=1
                    
                    act_unt = ((float(data['price_unit'])*100)/113)
                    pstr =  str(data['product']) +" -- " + str("%.2f" % data['quantity']) +" Units @" + str("%.2f" % act_unt) + "= "+ str("%.2f" % data['price_subtotal'])
                    sheet.write(row_number, col_number + 3, pstr,format4)
                    tmp = data['number']
                    tmp1 = data['amount_total']
                    row_number += 1
            
            
            
            elif 'lid' in data:
                if tmpd == data['move_name']:
                    sheet.write(row_number, col_number , " ",
                            format4)
                    sheet.write(row_number, col_number + 1, " ",
                            format4)
                else:
                    row_number += 1
                    sheet.write(row_number, col_number, str(data['ldate']), format4)
                    sheet.write(row_number, col_number + 1, data['move_name'],
                            format4)
                    sheet.write(row_number, col_number + 3, data['lname'],format4)
                    # sheet.write(row_number, col_number + 2, data['lcode'], format4)
                    # sheet.write(row_number, col_number + 3, data['partner_name'],
                    #             format4)
                   
                # sheet.write(row_number, col_number + 3, lines['lref'],format4)
                
                
                if data['accname'] == 'Account Receivable' and data['credit'] != 0 and data['debit'] == 0:
                    closing_balance = (closing_balance - data['credit'])
                    _logger.info('=============closing-1=============%s', closing_balance)
                    _logger.info('=============closing-1=============%s', data['credit'])
                elif data['accname'] == 'Account Receivable' and data['credit'] == 0 and data['debit'] != 0:
                    closing_balance = (closing_balance + data['debit'])
                    _logger.info('=============closing-2=============%s', closing_balance)
                    _logger.info('=============closing-2=============%s', data['debit'])
                
                if data['accname'] == 'Account Payable' and data['credit'] == 0 and data['debit'] != 0:
                    closing_balance = (closing_balance + data['debit'])
                    _logger.info('=============closing-3=============%s', closing_balance)
                    _logger.info('=============closing-3=============%s', data['debit'])
                
                elif data['accname'] == 'Account Payable' and data['credit'] != 0 and data['debit'] == 0:
                    closing_balance = (closing_balance - data['credit'])
                    _logger.info('=============closing-4=============%s', closing_balance)
                    _logger.info('=============closing-4=============%s', data['credit'])

                if data['accname'] == 'Account Receivable' or  data['accname'] == 'Account Payable':
                    sheet.write(row_number, col_number + 4, data['debit'], format4)
                    sheet.write(row_number, col_number + 5, data['credit'], format4)
                    sheet.write(row_number, col_number + 6, str("%.2f" % closing_balance), format4)
                tmpd = data['move_name']
                row_number += 1

        sheet.write(row_number, col_number + 3, "Closing Balance",format4)
        sheet.write(row_number, col_number + 6, str("%.2f" % closing_balance),format4)

        #path = ("/mnt/extra-addons/Partner_detailed_report.xls")
        path = ("/home/odoo/reports/Partner_detailed_report.xls")
        workbook.save(path)
        file = open(path, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        self.write({'state': 'get', 'file_name': out, 'invoice_data':'Partner_detailed_report.xls'})
        return {
               'type': 'ir.actions.act_window',
               'res_model': 'partner.detailed.reporting',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': self.id,
               'target': 'new',
            }                

    
    



                  
