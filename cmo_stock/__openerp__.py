# -*- coding: utf-8 -*-
{
    "name": "CMO :: Stock Extension",
    "summary": "",
    "version": "1.0",
    "category": "Warehouse Management",
    "description": """

    """,
    "website": "http://ecosoft.co.th",
    "author": "Tharathip C.",
    "license": "AGPL-3",
    "depends": [
        'stock_operating_unit',
        'purchase_operating_unit',
        'stock_account',
        'cmo_project',
        'cmo_operating_unit',
    ],
    "data": [
        'data/stock_data.xml',
        'security/cmo_stock_security.xml',
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        'views/report_stockpicking.xml',
        'views/stock_report.xml',
        'views/stock_valuation_history_view.xml',
    ],
    "application": False,
    "installable": True,
}
