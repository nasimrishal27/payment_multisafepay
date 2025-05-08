# -*- coding: utf-8 -*-
{
    'name': "Payment Provider: MultiSafePay",
    'version': '1.0',
    'depends': ['payment','website_sale','account'],
    'author': "Suni",
    'description': """
    """,
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_multisafepay_templates.xml',

        'data/payment_method_multisafepay.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

