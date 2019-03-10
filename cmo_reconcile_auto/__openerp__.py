# -*- coding: utf-8 -*-
{
    "name": "CMO :: Reconcile Auto",
    "summary": "Auto reconcile open item in various cases",
    "version": "1.0",
    "category": "Hidden",
    "description": """
By Odoo standard, only receivable/payable is reconciled when invoice->payment,
reconcilation also extened for all reconcilable account,
* Invoice -> Payment
    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'account_voucher',
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "application": False,
    "installable": True,
}
