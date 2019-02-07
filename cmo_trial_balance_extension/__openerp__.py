# -*- coding: utf-8 -*-
{
    "name": "CMO :: Trial Balance Export XLS",
    "summary": "",
    "version": "1.0",
    "category": "Accounting",
    "description": """
Add ability to export Trial Balance as xlsx
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_trial_balance_report",
        "pabi_utils",
    ],
    "data": [
        "xlsx_template/xlsx_template_wizard.xml",
        "xlsx_template/templates.xml",
        "xlsx_template/load_template.xml",
    ],
}
