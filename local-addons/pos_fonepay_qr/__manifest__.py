{
    'name': 'POS Fone Pay QR',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 10,
    'summary': 'Integrate your POS with a Fone Pay Dynamic Qr',
    'data': [
        'views/pos_payment_method_views.xml',
        # 'views/assets_stripe.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_fonepay_qr/static/**/*',
        ],
    },
    'license': 'LGPL-3',
}
