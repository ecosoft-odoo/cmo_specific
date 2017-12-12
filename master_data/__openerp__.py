# -*- coding: utf-8 -*-

{
    'name': "CMO Master Data",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    'version': '0.1.0',
    'depends': [
        'product',
        'hr_expense',
        'sale',
    ],
    'data': [
        'product/product.category.csv',
        'purchase/purchase.order.type.config.csv',
        'sale/sale_layout.category.csv',
        'users/hr.employee.csv',
        'level_validation/advance/level.validation.csv',
        'level_validation/clearing/level.validation.csv',
        'level_validation/expense/level.validation.csv',
        'level_validation/purchase/level.validation.csv',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
