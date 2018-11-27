# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 Readonly Groups',
    'summary': """
Readonly for following models,

- Expense
- Sales Order
- Purchase order
- Invoice
- Payment

    """,
    'author': 'Kitti U.',
    'website': 'http://ecosoft.co.th',
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'depends': [
        'sale',
        'purchase',
        'account',
        'account_voucher',
        'hr_expense',
    ],
    'data': [
        'security/readonly_group.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
