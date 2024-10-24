# -*- coding: utf-8 -*-
{
    'name': "PoS KOT",
    'description': """
        POS KOT 
    """,
    'author': "Smarten Technologies",
    'website': "https://www.smarten.com.np",
    'category': 'POS',
    'version': '17.1',
    'depends': ['point_of_sale', 'pos_preparation_display'],
    'data': [
        "views/kot.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
    'sequence': 9999
}
