# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class Cars(models.Model):
    _name = 'cmo_fm_services.cars'
    _inherit = 'mail.thread'

    code = fields.Char(readonly=True)
    event = fields.Char(string='Event',required=True)
    place = fields.Char(string='Location',required=True)
    task = fields.Char(string='Task',required=True)
#    car = fields.Selection([('Van', 'Van'), ('Pickup Truck', 'Pickup Truck'),  ],default='Van',required=True,string='Car Type',)
    
    start_date = fields.Datetime(string="Start Date", default=lambda self: fields.datetime.now(),copy=False,required=True)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
#    end_date = fields.Datetime(string="End Date", store=True, compute='_get_end_date', inverse='_set_end_date',copy=False)
    end_date = fields.Datetime(string="End Date", default=lambda self: fields.datetime.now(),copy=False,required=True)
    
#    hours = fields.Float(string="Duration in hrs.", compute='_get_hours', inverse='_set_hours')

    number = fields.Integer(string='Passenger Numbers',required=True)
    passenger = fields.Text(string='Passenger Names')                       
    operating_unit = fields.Many2one('operating.unit', string='Operating Unit', default=lambda self: self.env.user.default_operating_unit_id,copy=False,readonly=True)
    by = fields.Many2one('res.users', default=lambda self: self.env.user,copy=False,readonly=True)
    
#    current_employee = fields.Many2one('res.users', compute='_get_current_employee')
#    @api.depends()
#    def _get_current_employee(self):
#        for rec in self:
#            rec.current_employee = self.env.user.partner_id.employee_id
#            self.write({'current_employee' : self.env.user.partner_id.employee_id})
    
    
    project = fields.Many2one(
        'project.project',
        string='Project',
        domain=lambda self: self._get_domain_project(),
    )
    
    note = fields.Text(string='Note')
    
    state = fields.Selection([
        ('draft', "New"),
        ('confirmed', "Waiting to Reserved"),
        ('done', "Reserved"),
        ('cancelled', "Cancelled"),
        
    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        a = str(self._uid)
        b = str(self.by.id)
        if (a == b):
            self.state = 'confirmed'
        else:
            raise ValidationError(_('You are not owner document.'))
        
    @api.multi
    def action_done(self):
        self.state = 'done'
        
    @api.multi
    def action_cancelled(self):
            self.state = 'cancelled'
    
    @api.multi
    def name_get(self):
        res = []
        for c in self:
            name = c.event or '/'
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

    @api.model
    def create(self,vals):
        ctx = {'fiscalyear_id': self.env['account.fiscalyear'].find()}
        vals['code'] = \
            self.env['ir.sequence'].with_context(ctx).get('car.no')
        result = super(Cars, self).create(vals)
        return result
    
    @api.multi
    def copy(self):
        raise ValidationError(_('It not possible to duplicate same date the record, pls. create a new one.'))
        
    @api.multi
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        envir = self.env['cmo_fm_services.cars'].search([('id', '!=', self.id),('state', '=', 'done')])
        for record in envir:
            start_self = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
            end_self = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
            start_rec = datetime.strptime(record.start_date, "%Y-%m-%d %H:%M:%S")
            end_rec = datetime.strptime(record.end_date, "%Y-%m-%d %H:%M:%S")

            if (start_self >= end_self):
                raise ValidationError(_("[Start Date] must be less than [End Date], pls. change your times."))
            
            if( ((start_self >= start_rec) and (end_self <= end_rec)) 
               or ((start_self < start_rec) and (end_self > start_rec)) 
               or ((start_self < end_rec) and (end_self > end_rec)) 
              ):
                raise ValidationError(_('It not possible to duplicate [times] in your reserve, pls. change your [times] .'))
    
    
#    @api.multi
#    @api.constrain('start_date', 'end_date')
#    def _check_due_date(self):
#        for rec in self:
#            if rec.start_date > rec.end_date:
#                raise ValidationError(
#                    _('Start Date must before End Date.'))
    
#    @api.depends('start_date', 'duration')
#    def _get_end_date(self):
#        for r in self:
#            if not (r.start_date and r.duration):
#                r.end_date = r.start_date
#                continue
#
#            start = fields.Datetime.from_string(r.start_date)
#            duration = timedelta(days=r.duration, seconds=-1)
#            r.end_date = start + duration
#
#    def _set_end_date(self):
#        for r in self:
#            if not (r.start_date and r.end_date):
#                continue
#
#            start_date = fields.Datetime.from_string(r.start_date)
#            end_date = fields.Datetime.from_string(r.end_date)
#            r.duration = (end_date - start_date).days + 1
            
#            
#    @api.depends('duration')
#    def _get_hours(self):
#        for r in self:
#            r.hours = r.duration * 24
#            
#    def _set_hours(self):
#        for r in self:
#            r.duration = r.hours / 24
