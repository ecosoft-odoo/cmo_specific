# -*- coding: utf-8 -*-

{
    'name': "CMO :: Sale Extension",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    "version": "1.0",
    'depends': [
        'sale',
        'report',
        'sale_layout',
        'sale_stock',
        'sale_margin',
        'sale_invoice_plan',
        'sale_split_quote2order',
        'cmo_account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sale_data.xml',
        # 'data/product_data.xml',
        'wizard/cal_manage_fee_view.xml',
        'views/sale_view.xml',
        'views/master_data_view.xml',
        'views/product_view.xml',
        'views/sale_layout_view.xml',
        'views/account_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
