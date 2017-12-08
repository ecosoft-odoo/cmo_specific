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
    ],
    "data": [
        'views/product_category_view.xml',
        'views/account_asset_view.xml',
        'views/account_asset_profile_view.xml',
    ],
    "application": False,
    "installable": True,
}
