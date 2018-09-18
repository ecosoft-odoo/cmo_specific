# -*- coding: utf-8 -*-
{
    'name': 'CMO :: Accounting Reports',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Saran Lim.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'pabi_utils',
        'account',
        'report_xls',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'data/menu.xml',
        'reports/report_account_common.xml',
        'reports/xlsx_report_input_tax.xml',
        'reports/xlsx_report_output_tax.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
