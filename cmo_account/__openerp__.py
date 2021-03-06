# -*- coding: utf-8 -*-
{
    "name": "CMO :: Account Extension",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
    """,
    "website": "http://ecosoft.co.th",
    "author": "Tharathip C., Phongyanon Y.",
    "license": "AGPL-3",
    "depends": [
        'l10n_th_account',
        'account',
        'account_voucher',
        'account_operating_unit',
        'account_bank_payment',
        'hr_expense_advance_clearing',
        'sale_layout',
        'project',
    ],
    "data": [
        'data/report_data.xml',
        'data/security.xml',
        'wizard/account_tax_detail_view.xml',
        'wizard/edit_desc.xml',
        'views/account_invoice_view.xml',
        'views/product_view.xml',
        'views/account_view.xml',
        'views/account_voucher_view.xml',
        'views/account_bank_receipt_view.xml',
        'views/account_wht_cert.xml',
        'views/res_company.xml',
    ],
    "application": False,
    "installable": True,
}
