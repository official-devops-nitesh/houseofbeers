{
    "name": "POS Receipt Bill",
    "version": "17.1",
    "category": "POS",
    "summary": "POS Receipt Bill",
    "author": "Smarten Technologies",
    "website": "https://www.smarten.com.np",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_receipt_bill/static/src/**/*',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': True,
}
