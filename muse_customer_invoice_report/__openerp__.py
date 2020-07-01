# -*- coding: utf-8 -*-

{
    'name': "MUSE :: Muse Invoice Report Jasper (PDF)",
    'summary': "",
    "description": """

* account invoice and account voucher report jasper

    """,
    'author': "Phongyanon Y.",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    "version": "1.0",
    'depends': [
        'account_supplier_billing',
        'report',
        'cmo_account',
        'l10n_th_amount_text',
        'cmo_company_enhance',
    ],
    'data': [
        'report/report_data.xml',
        'report/print_document_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
