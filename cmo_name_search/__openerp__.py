# -*- coding: utf-8 -*-
{
    "name": "CMO :: CMO - Name Search",
    "version": "1.0",
    "description": """

- All configuration for name_search in one place
- Extend search on invoice/payment/journal entry, i.e., PV001-PV005,PV006,PV007

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Ecosoft",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'cmo_sale',
    ],
    "data": [
        'ir.model.csv',
    ],
}
