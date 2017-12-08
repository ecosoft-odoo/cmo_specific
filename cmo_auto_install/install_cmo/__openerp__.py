# -*- coding: utf-8 -*-
{
    "name": "CMO :: Install CMO Addons",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "description": """


    """,
    "website": "http://203.146.226.60",
    "author": "Phongyanon Y.,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        # Standard Module for most SMEs.
        'sale',
        "purchase",
        "purchase_requisition",
        "stock",
        "sale_stock",
        "project",
        "account",
        # Thai Localization Module
        "sale_split_quote2order",
        "sale_invoice_plan",
        "purchase_invoice_plan",
        "account_billing",
        "account_billing_hook_recompute_vline",
        "l10n_th_account",
        "account_bank_receipt",
        "l10n_th_tax_report",
        "jasper_reports",
        "account_invoice_check_tax_lines_hook",
        "l10n_th_account_pnd_form",
        "l10n_th_account_tax_detail",
        "l10n_th_address",
        # "stock_asset",
        "account_financial_report",
        "hr_expense_advance_clearing",
        "purchase_analytic_plans",
        "sale_analytic_plans",
        # Additional Module
        "sale_operating_unit",
        "purchase_operating_unit",
        "account_operating_unit",
        "sale_layout",
        "web_translate_dialog",
        "sale_discount_total",
        "account_asset_management",
    ],
    'pre_init_hook': 'pre_init_hook',
}
