# -*- coding: utf-8 -*-
from openerp import models, fields, api


# def filter_print_report(res, reports):
#     action = []
#     if res.get('toolbar', {}) and res.get('toolbar').get('print', False):
#         for act in res.get('toolbar').get('print'):
#             if act.get('report_name') in reports:
#                 continue
#             action.append(act)
#         res['toolbar']['print'] = action
#     return res
#
#
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_position_name = fields.Char(
        compute='_compute_related_job_name',
    )
    approval_position_name = fields.Char(
        compute='_compute_related_job_name',
    )

    @api.multi
    def _compute_related_job_name(self):
        for rec in self:
            sale_job_id = rec.sudo().user_id.partner_id.employee_id.job_id
            approval_job_id = rec.sudo().approval_id.partner_id.employee_id.job_id
            rec.update({
                'sale_position_name': sale_job_id.name,
                'approval_position_name': approval_job_id.name,
            })
