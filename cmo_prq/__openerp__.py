# -*- coding: utf-8 -*-
{
    'name': "PRQ",
    'summary': "Add field PRQ for some document need boss approve before"
               "(Purchase Order and Expense)",
    'author': "Saran Lim.",
    'website': "http://ecosoft.co.th",
    'category': 'Purchase Management',
    "version": "2.0",
    'depends': [
        'l10n_th_doctype_base',
        'purchase_invoice_plan',
        'hr_expense_auto_invoice',
        'operating_unit',
        'cmo_purchase_level_validation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/prq_security.xml',
        'security/prq_security_rule.xml',
        'data/ir_sequence_data.xml',
        'data/doctype_data.xml',
        'views/purchase_view.xml',
        'views/purchase_prq_view.xml',
        'views/account_invoice.xml',
        'views/hr_expense_view.xml',
        'wizards/expense_create_supplier_invoice_wizard.xml',
        'wizards/print_prq_wizard.xml',
        'reports/jasper_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
