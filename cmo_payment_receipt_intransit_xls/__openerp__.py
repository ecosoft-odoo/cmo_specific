# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Payment Receipt Intransit Excel reporting',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'depends': [
        'account',
        'report_xls',
    ],
    'data': [
        'wizard/wiz_payment_receipt_intransit_report.xml',
    ],
    'installable': True,
}
