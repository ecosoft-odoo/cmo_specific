# -*- coding: utf-8 -*-
import random
from datetime import timedelta
from openerp import models, fields, api, _

class Letter(models.Model):
    _name = 'outbound_letter.letter'
    _inherit = 'mail.thread'

    code = fields.Char(readonly=True)
    # project = fields.Char(required=True)
    # project = fields.Many2one(
      #  'project.project',
    #    index=True
    #)
    
    #project = fields.Many2one(
        #'project.project',
        #string='Project',
        #domain=lambda self: self._get_domain_project(),
    #)
    
    #project = fields.Char(
        #related='analytic_account_id.code',
        #store=True
    #)
    date = fields.Date(required=True, default=lambda self: fields.Date.context_today(self))
    subject = fields.Char(required=True)
    to = fields.Char(required=True)
    #type = fields.Selection([('Contract', 'Contract'), ('Memo', 'Memo')])
    type = fields.Selection([('Letter', 'Letter'), ('Contract', 'Contract'), ('Memo', 'Memo'), ],default='Letter',required=True)
    by = fields.Many2one('hr.employee', default=lambda self: self.env.user.partner_id.employee_id,readonly=True,copy=False)
    operating_unit = fields.Many2one('operating.unit', string='Operating Unit', default=lambda self: self.env.user.default_operating_unit_id,readonly=True,copy=False)
    #note = fields.Text()
    project = fields.Text()
    received = fields.Boolean(string='Recieved (for Legal only)', default=False)
#    project_id = fields.Char(related='projects.name', store=True)

#    project_analytics = fields.Char(
#        compute='_compute_code'
#    )
#
#    def _compute_code(self):
#        for record in self:
#            record.project_analytics = '%s' % record.project_id
#            return record.project_analytics

    # project_analytics = fields.Char(
    #     related='projects.name', store=True
    # )
    # project_analytics = fields.Many2one(
    #     'account.analytic.account',
    #     'name',
    #     copy=True
    # )


    # aaa = fields.Char(compute='_compute_code')

    #@api.multi
    #def name_get(self):
        #res = []
        #for project in self:
            #name = project.name or '/'
            #if name and project.code:
                #name = '[%s] %s' % (project.code, name)
            #res.append((project.id, name))
        #return res

    @api.multi

    def name_get(self):
        res = []
        for c in self:
            name = c.project or '/'
            if name and c.code:
                name = '[%s] %s' % (c.code, name)
            res.append((c.id, name))
        return res
    
    
    @api.model
    def _get_domain_project(self):
        operating_unit_ids = self.env.user.operating_unit_ids.ids
        domain = [
            ('operating_unit_id', 'in', operating_unit_ids),
        ]
        return domain

    #project_related = fields.Many2one(
        #'project.project',
        #states={'done': [('readonly', True)]},
        #domain=[
        #    ('state', 'not in', ['draft', 'pending', 'cancelled', 'close']),
        #],
        #required=True,
        #index=True,
    #)
    #state = fields.Selection(
    #    [('draft', 'Draft'),
    #     ('done', 'Done'),
    #     ('cancel', 'Cancel')],
    #    string='Status',
    #    default='draft',
    #    readonly=True,
    #)



    #@api.multi
    #def _compute_code(self):
        #for record in self:
            #record.code = str(random.randint(1,1e6))

    @api.model

    def create(self,vals):
        ctx = {'fiscalyear_id': self.env['account.fiscalyear'].find()}
        vals['code'] = \
            self.env['ir.sequence'].with_context(ctx).get('code.no')
        #vals['code'] = self.env['ir.sequence'].next_by_code('code.no') or '/'
        result = super(Letter, self).create(vals)
        return result



