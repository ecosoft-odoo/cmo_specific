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
    ],
    'data': [
        'views/hr_level_validation_view.xml',
        'workflow/hr_level_validation_workflow.xml',
        'data/level_validation_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
