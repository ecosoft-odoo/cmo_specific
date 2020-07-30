# -*- coding: utf-8 -*-
{
    'name': "cmo_fm_services",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Adinan H.",
    'website': "https://erp.cmo-group.com",
    'category': 'Uncategorized', 
    'version': '0.1',
    'depends': [
        'base',
        'pabi_utils',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # car center
        'data/car_sequence.xml',
        'views/car.xml',
        'views/car_workflow.xml',
        
        # meeting room
        'data/room_sequence.xml',
        'views/room.xml',
        'views/room_workflow.xml',
    ],
    'demo': [
    ],
}
