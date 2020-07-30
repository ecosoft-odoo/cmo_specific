# -*- coding: utf-8 -*-
{
    'name': "Outbound Letter",

    'summary': """
    Module to create Outbound Letter of CMO projects.
        """,

    'description': """
        Outbound Letter for CMO Public Company Limited
    """,

    'author': "Adinan H.",
    'website': 'https://erp.cmo-group.com',

    'category': 'CMO',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        #'mail',
        'pabi_utils',
        #'l10n_th_doctype_base',
    ],

    # always loaded
    'data': [
        'data/letter_sequence.xml',
        #'security/ir.model.access.csv',
        'views/letter.xml',
        'views/letter_workflow.xml',

    ],

    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}