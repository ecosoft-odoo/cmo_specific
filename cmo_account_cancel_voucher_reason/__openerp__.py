# -*- coding: utf-8 -*-
{
    'name': 'CMO :: Adjust Payment Cancel Reason',
    'version': '8.0.1.0.0',
    'author': "Tharathip C.",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When an payment is canceled, system will check bank receipt / payment and
    show error when found at least one.
    """,
    'depends': [
        'account_voucher_cancel_reason',
        'account_bank_receipt',
        'account_bank_payment',
    ],
    'demo': [],
    'data': [],
    'auto_install': False,
    'installable': True,
}
