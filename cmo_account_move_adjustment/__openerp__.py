# -*- coding: utf-8 -*-
{
    'name': 'Account Move - Adjustment Types',
    'version': '8.0.1.0.0',
    'author': 'Tharathip C.',
    'summary': 'Journal Entries Adjustment Doctypes',
    'description': """
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'l10n_th_fields',
    ],
    'demo': [],
    'data': [
        'wizards/create_journal_entry_wizard.xml',
        'wizards/reconcile_unbilled_items.xml',
        'views/account_invoice_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
