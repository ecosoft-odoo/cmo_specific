# -*- coding: utf-8 -*-
{
    "name": "CMO :: Project Actual Budget Report",
    "summary": "",
    "version": "1.0",
    "category": "Project",
    "description": """
    """,
    "website": "http://ecosoft.co.th",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'cmo_project',
        'web_tree_dynamic_colored_field',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/project_view.xml',
        'wizard/project_search_view.xml',
    ],
    "application": False,
    "installable": True,
}
