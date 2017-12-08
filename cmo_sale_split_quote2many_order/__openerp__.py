# -*- coding: utf-8 -*-

{
    'name': "CMO :: Sale Quotation split to many order",
    'summary': "Sale Quotation split to many order for miltiple customer",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    "version": "1.0",
    'depends': [
        'sale',
        'cmo_sale',
        'sale_split_quote2order',
        'cmo_sale_discount_total_enhance',
    ],
    'data': [
        'views/sale.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
