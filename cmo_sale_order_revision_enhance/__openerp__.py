# -*- coding: utf-8 -*-

{
    'name': "CMO :: Sale Order Revision Enhance",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    "version": "1.0",
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'demo': [
    ],
    'active': False,
    'installable': True,
    'post_init_hook': 'populate_unrevisioned_name',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
