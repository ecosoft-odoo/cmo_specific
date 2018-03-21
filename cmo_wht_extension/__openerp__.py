# -*- coding: utf-8 -*-

{
    'name': "Withholding Tax Cert on Expense",
    'summary': "Added support for creation of withholding tax cert on expense",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'l10n_th_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/action.xml',
        'views/account_wht_cert.xml',
        'views/hr_expense_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
