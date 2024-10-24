# -*- coding: utf-8 -*-
{
    'name': 'IRD Sales/Purchase Report Extension',
    'version': '17.0',
    'category': 'Accounts',
    'summary': ''' IRD compliance Sales/Purchase Report Extension''',
    'author': 'Smarten Technologies Pvt. Ltd.',
    'license': "OPL-1",
    'depends': [
        'base',
        'account',
        'sale_management',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/ird_sales_purchase_report_ext_view.xml',
    ],
    'demo': [],
    'auto_install': False,
    'installable': True,
    'application': True
}
