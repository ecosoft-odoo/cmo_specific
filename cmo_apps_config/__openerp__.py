# -*- coding: utf-8 -*-
{
    "name": "CMO Final Apps Config",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """
This module is meant to be updated last
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'cmo_account',
        'cmo_purchase',
        'cmo_sale',
        'cmo_hr',
    ],
    "data": [
        'security/model_no_delete.xml',
        'security/model_readonly.xml',
        'views/user_setting.xml',
        'scripts/del_lang_th.xml',
    ],
}
