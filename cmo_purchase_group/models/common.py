# -*- coding: utf-8 -*-
from openerp import api
from lxml import etree


class Common(object):

    @api.model
    def set_right_readonly_group(self, res):
        root = etree.fromstring(res['arch'])
        root.set('create', 'false')
        root.set('edit', 'false')
        root.set('delete', 'false')
        res['arch'] = etree.tostring(root)
        return res
