# -*- coding: utf-8 -*-

{
    'name': "CMO :: Purchase Extension",
    'summary': "",
    'author': "Tharathip C.",
    'website': "http://ecosoft.co.th",
    'category': 'Purchase Management',
    "version": "1.0",
    'depends': [
        'purchase_operating_unit',
        'purchase_invoice_plan',
        'account_auto_fy_sequence',
        'cmo_sale',
        'project',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'reports/purchase_report.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
