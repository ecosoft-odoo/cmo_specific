# -*- coding: utf-8 -*-
{
    'name': 'CMO :: Purchase Invoice Plan Extension',
    'version': '1.0',
    'author': 'Tharathip C.',
    'summary': 'Purchase Invoice Plan',
    'description': """
Purchase Invoice Plan
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'purchase_invoice_plan',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
    ],
    'test': [],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
