# -*- coding: utf-8 -*-

{
    'name': "CMO :: Purchase Level Validation",
    'summary': "",
    'author': "Phongyanon Yan.",
    'website': "http://ecosoft.co.th",
    'category': 'Purchase Management',
    "version": "1.0",
    'depends': [
        'purchase',
        'purchase_operating_unit',
        'cmo_level_validation',
        'cmo_project',
    ],
    'data': [
        'security/purchase_security.xml',
        'views/purchase_level_validation_view.xml',
        'workflow/purchase_level_validation_workflow.xml',
        # 'data/level_validation_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
