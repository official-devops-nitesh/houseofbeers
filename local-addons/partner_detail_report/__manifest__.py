
# -*- coding: utf-8 -*-
{
    'name': 'Partner Detailed Report',
    'version': '17.0',
    'summary': """Partner Detailed Report""",
    'description': """Partner Detailed Report""",
    'category': 'Accounting',
    'author': 'Smarten Technologies Pvt. Ltd.',
    'depends': ['base', 'account', 'report_xlsx', 'web'],
    'website': 'https://www.smarten.com.np',
    'data': [
        'wizard/rep_account_account.xml',
        'wizard/xlsx_partner_rep.xml',
        'reports/day_book_report.xml',
        # 'reports/day_book_template.xml',
        'reports/partner_detail_template.xml'
    ],
    'qweb': [],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
