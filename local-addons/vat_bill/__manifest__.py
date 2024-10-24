# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'VAT BILL IRD INTEGRATION',
    'version': '17.0',
    'summary': 'Nepali VAT Bill/ IRD Integration',
    'description': "Nepali VAT System",
    'category': 'Accounting',
    'author': 'Smarten Technologies Pvt. Ltd.',
    'website': 'https:smarten.com.np',
    'license': 'AGPL-3',
    'data': [

        'report/vat_invoice_pdf.xml',
        'report/vat_sales_invoice_pdf.xml',
        'view/res_cmpny.xml',
        'view/account_move_inherited.xml',
        'view/ir_actions_report_xml.xml',
        'view/res_config_view.xml',
        'data/data.xml',
    ],
    'depends': ['base', 'sale_management', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'images': ['static/description/banner.png'],

}


