# -*- coding: utf-8 -*-
{
    'name': "pos_merge_table_order",
    'description': """
        POS Merge 2 or more table orders merge into one table
    """,
    'author': "Smarten Technologies",
    'website': "https://www.smarten.com.np",
    'category': 'POS',
    'version': '17.1',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_merge_table_order/static/src/**/*',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': True,
}
