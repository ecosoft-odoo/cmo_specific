# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cost Control Sheet Excel reporting',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'depends': [
        'cmo_project',
        'cmo_hr',
        'cmo_sale',
        'cmo_purchase',
        'report_xls',
    ],
    'data': [
        'views/project_view.xml',
        'wizard/wiz_cost_control_sheet_report.xml',
    ],
    'installable': True,
}
