# -*- coding: utf-8 -*-
# Copyright (c) 2022-Present Mentis Consultancy Services. (<https://mcss.odoo.com>)

{
    'name': 'Mastercard(MPGS) Payment Provider',
    'category': 'Accounting/Payment Providers',
    'version': '16.0.1.0',
    'license': 'OPL-1',
    'author': 'Mentis Consultancy Services',
    'website': 'https://mcss.odoo.com',
    'support': 'support@mcshelp.odoo.com',
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_mpgs_templates.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_mastercard_mpgs/static/src/js/payment_form.js',
        ],
    },
    'images': [
        'static/description/banner.gif',
    ],
    'application': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'description': """Mastercard(MPGS) Payment Provider""",
    'price': 89,
    'currency': 'usd',
    'summary': '''
        Payment Provider: Mastercard(MPGS) Payment Gateway
        Online Payment
        E-commerce Payment
        Invoice Payment
        Master Card Payment MPGS
        Visa Card Payment
        MADA Card Payment
        3D Secure Payment  
    '''
}
