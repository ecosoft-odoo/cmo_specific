# -*- coding: utf-8 -*-
{
    "name": "CMO :: Account Report Webkit Extension",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
    """,
    "website": "http://ecosoft.co.th",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'account_financial_report_webkit',
        'account_financial_report_webkit_xls',
    ],
    "data": [
        'wizard/general_ledger_wizard_view.xml',
        'reports/report.xml',
    ],
    "application": False,
    "installable": True,
}
