# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) Avoin.Systems 2020

# noinspection PyStatementEffect
{
    "name": "POS Bill IRD",
    "version": "17.0.1.0.0",
    "author": "Smarten Technologies",
    "category": "Localization",
    "website": "https://www.smarten.com.np",
    "license": "AGPL-3",
    "images": ["static/description/icon.png"],
    "depends": ['account'
   ],
    "data": [
        "views/account_move_templates.xml",
        "data/report_paperformat_data.xml",  # Only after the template
    ],
    "summary": "IRD POS Bill",
}
