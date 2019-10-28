# -*- coding: utf-8 -*-
{
    'name': 'CMO :: Customer Receipt Voucher Report',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'account_voucher',
    ],
    'data': [
        'data/report_paperformat_data.xml',
        'data/report_data.xml',
        'security/ir.model.access.csv',
        'report/report_templates.xml',
        'report/report_customer_receipt_voucher.xml',
        'wizards/customer_receipt_voucher_wizards.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
