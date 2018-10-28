# -*- coding: utf-8 -*-
{
    "name": "CMO :: Final Configs",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "account_voucher",
        "purchase",
        "purchase_requisition",
        "stock",
        "sale",
    ],
    "data": [
        'security/model_no_delete.xml',
        'security/model_readonly.xml',
        'scripts/del_lang_th.xml',
    ],
}
