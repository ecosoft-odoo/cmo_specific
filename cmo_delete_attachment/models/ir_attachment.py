# -*- coding: utf-8 -*-
from openerp import models, SUPERUSER_ID


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids, context=context):
            if uid == item.user_id.id:
                return super(ir_attachment, self).unlink(cr, SUPERUSER_ID, ids, context=context)
            else:
                return super(ir_attachment, self).unlink(cr, uid, ids, context=context)
