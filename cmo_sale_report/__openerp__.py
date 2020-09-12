# -*- coding: utf-8 -*-

{
    'name': "CMO :: Sale Report Jasper (PDF)",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    "version": "1.0",
    'depends': [
        'sale',
        'sale_split_quote2order',
        'cmo_sale_discount_total_enhance',
        'report',
        'cmo_company_enhance',
    ],
    'data': [
        'report/report_saleorder.xml',
        'views/sale_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
