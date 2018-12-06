# -*- coding: utf-8 -*-

{
    'name': "CMO :: HR Level Validation",
    'summary': "",
    'author': "Phongyanon Yan.",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    "version": "1.0",
    'depends': [
        'hr_expense_auto_invoice',
        'hr_expense_advance_clearing',
        'hr_expense_operating_unit',
        'cmo_level_validation',
        'cmo_project',
        'hr_expense_cancel_reason',
        'hr_expense_auto_invoice',
    ],
    'data': [
        # 'data/level_validation_data.xml',  # Moved to master data
        'security/ir_rule.xml',
        'security/security.xml',
        'workflow/hr_level_validation_workflow.xml',
        'wizard/edit_unit_amount.xml',
        'wizard/edit_analytic_account.xml',
        'views/hr_level_validation_view.xml',
        'views/product_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
