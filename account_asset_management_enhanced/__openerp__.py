# -*- coding: utf-8 -*-
{
    "name": "Account Asset Management Enhanced",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
    """,
    "website": "http://ecosoft.co.th",
    "author": "Phongyanon Y.",
    "license": "AGPL-3",
    "depends": [
        'account_asset_management',
        'account_auto_fy_sequence',
        'account_operating_unit',
        'account_cancel_reversal',
        'account_debitnote',
    ],
    "data": [
        'views/product_category_view.xml',
        'views/account_asset_view.xml',
        'views/account_asset_profile_view.xml',
        'views/account_invoice_view.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
    "application": False,
    "installable": True,
}
