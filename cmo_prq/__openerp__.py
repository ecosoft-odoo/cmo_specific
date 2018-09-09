# -*- coding: utf-8 -*-
{
    'name': "PRQ",
    'summary': "Add field PRQ for some document need boss approve before"
               "(Purchase Order and Expense)",
    'author': "Saran Lim.",
    'website': "http://ecosoft.co.th",
    'category': 'Purchase Management',
    "version": "1.0",
    'depends': [
        'l10n_th_doctype_base',
        'purchase_invoice_plan',
        'hr_expense_auto_invoice',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/doctype_data.xml',
        'views/purchase_view.xml',
        'views/purchase_prq_view.xml',
        'views/account_invoice.xml',
        'views/hr_expense_view.xml',
        'wizards/expense_create_supplier_invoice_wizard.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
