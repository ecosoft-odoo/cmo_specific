# -*- coding: utf-8 -*-
{
    'name': 'CMO Purchase Report',
    'version': '8.0.1.0.1',
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'purchase',
        'cmo_company_enhance',
    ],
    'data': [
        "jasper_data.xml",
        'views/purchase_config_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
