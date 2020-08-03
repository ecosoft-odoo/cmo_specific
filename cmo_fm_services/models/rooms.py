# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class Rooms(models.Model):
    _name = 'cmo_fm_services.rooms'
    _inherit = 'mail.thread'

    code = fields.Char(string='Booking Number',readonly=True)
    subject = fields.Char(string='Subject',required=True)
    room = fields.Selection([ 
                             ('RedCurtainRoom', '1F - ห้องม่านแดง'),
                             ('LeatherRoom', '1F - ห้องหนัง'),
                             ('SquareRoom', '1F - ห้องเหล็ก (สี่เหลี่ยม)'),
                             ('Poon', '3F - ห้องปูน'),
                             ('MeetingRoom1', '3F - Meeting 1'),
                             ('MeetingRoom2', '3F - Meeting 2'),
                             ('MeetingRoom3', '3F - Meeting 3'),
                             ('MeetingRoom4', '3F - Meeting 4'),
                             ('MeetingRoom5', '3F - Meeting 5'),
                             ('MeetingRoom6', '3F - Meeting 6'),
                             ('MeetingRoom7', '3F - Meeting 7'),
                             ('MeetingRoom8', '3F - Meeting 8,9'),
                             ('MeetingRoom10', '3F - Meeting 10'),
                             ('MeetingRoom11', '3F - Meeting 11'),
                             ('GuestRoom', '3F - Meeting 12 (ห้องรับรอง)'),
                             ('TrainingRoom', '3F - Training Room'),
                             ('MusicRoom', 'ห้องซ้อมดนตรี'),
                             
                            ],default='MeetingRoom1',required=True,string='Room',)
    
    start_date = fields.Datetime(string="Start", default=lambda self: fields.datetime.now(),copy=False,required=True)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    end_date = fields.Datetime(string="End", default=lambda self: fields.datetime.now(),copy=False,required=True)
    
    number = fields.Integer(string='Attendee Numbers')
    attendee = fields.Text(string='Attendee Names')     
    by = fields.Many2one('res.users', default=lambda self: self.env.user,copy=False,readonly=True)
    operating_unit = fields.Many2one('operating.unit', string='Operating Unit', default=lambda self: self.env.user.default_operating_unit_id,copy=False,readonly=True)
    
    project = fields.Many2one(
        'project.project',
        string='Project',
        domain=lambda self: self._get_domain_project(),
    )
    
    equipment = fields.Text(string='Equipment(s)')
    note = fields.Text(string='Note')
    
    state = fields.Selection([
        ('draft', "New"),
#        ('confirmed', "Waiting to Reserved"),
        ('done', "Reserved"),
        ('cancelled', "Cancelled"),
        
    ], default='draft')
    
    @api.multi
    @api.constrains('start_date', 'end_date', 'room')
    def _check_date(self):
        envir = self.env['cmo_fm_services.rooms'].search([('id', '!=', self.id),('state', '=', 'done')])
        for record in envir:
            start_self = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
            end_self = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")
            start_rec = datetime.strptime(record.start_date, "%Y-%m-%d %H:%M:%S")
            end_rec = datetime.strptime(record.end_date, "%Y-%m-%d %H:%M:%S")
            
            if (start_self >= end_self):
            	raise ValidationError(_("Start must be less than End, pls. change your time."))
       	 
        	if (self.room == record.room):
            	if ( ((start_self >= start_rec) and (end_self <= end_rec)) or ((start_self < start_rec) and (end_self > start_rec)) or ((start_self < end_rec) and (end_self > end_rec)) ):
                	raise ValidationError(_("It not possible to duplicate room in your reserve, pls. change your room or times."))
            
#             if (self.room == record.room):
                
#                 if ((start_self.date() > start_rec.date() and end_self.date() < end_rec.date())
#                     or (start_self.date() <= start_rec.date() and end_self.date() >= end_rec.date())):
#                     if ((start_self.time() > start_rec.time() and start_self.time() < end_rec.time())
#                         or (end_self.time() > start_rec.time() and end_self.time() < end_rec.time())
#                         or (start_self.time() <= start_rec.time() and end_self.time() >= end_rec.time())):
#                         raise ValidationError(_("1Duplicate reserve in room : " + record.room + " ["+self.start_date + "-" + self.end_date+"], pls. change your room or time."))
                        
#                if start_self.date() >= start_rec.date() and end_self.date() <= end_rec.date():
#                    if ((start_self.time() > start_rec.time() and start_self.time() < end_rec.time())
#                        or (end_self.time() > start_rec.time() and end_self.time() < end_rec.time())
#                        or (start_self.time() <= start_rec.time() and end_self.time() >= end_rec.time())):
#                        raise ValidationError(_("Duplicate reserve in room : " + record.room + " ["+self.start_date + "-" + self.end_date+"], pls. change your room or time."))

#            if (self.room == record.room):
#                if start_self.date() == start_rec.date() and start_self.date() == end_rec.date():
#                    if ((start_self.time() > start_rec.time() and start_self.time() < end_rec.time())
#                        or (end_self.time() > start_rec.time() and end_self.time() < end_rec.time())
#                        or (start_self.time() <= start_rec.time() and end_self.time() >= end_rec.time())):
#                        raise ValidationError(_("Duplicate reserve in room : " + record.room + " ["+self.start_date + "-" + self.end_date+"], pls. change your room or time."))
                        
#             if (self.room == record.room):
#                if start_self.date() >= start_rec.date() and end_self.date() <= end_rec.date():
#                    if ((start_self.time() > start_rec.time() and start_self.time() < end_rec.time())
#                        or (end_self.time() > start_rec.time() and end_self.time() < end_rec.time())
#                        or (start_self.time() <= start_rec.time() and end_self.time() >= end_rec.time())):
#                        raise ValidationError(_("Duplicate reserve in room : " + record.room + " ["+self.start_date + "-" + self.end_date+"], pls. change your room or time."))

    @api.multi
    def action_draft(self):
        self.state = 'draft'

#    @api.multi
#    def action_confirm(self):
#        a = str(self._uid)
#        b = str(self.by.id)
#        if (a == b):
#            self.state = 'confirmed'
#        else:
#            raise ValidationError(_('You are not owner document.'))
        
    @api.multi
    def action_done(self):
        self.state = 'done'
        
    @api.multi
    def action_cancelled(self):
        a = str(self._uid)
        b = str(self.by.id)
        if (a == b):
            self.state = 'cancelled'
#            raise ValidationError(_('You are owner document.'))
        else:
            raise ValidationError(_('You are not owner document.'))
        
    
    @api.multi
    def name_get(self):
        res = []
        for c in self:
            name = c.subject or '/'
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
            self.env['ir.sequence'].with_context(ctx).get('room.no')
        result = super(Rooms, self).create(vals)
        return result
    
    @api.multi
    def copy(self):
        raise ValidationError(_('It not possible to duplicate same date & room, pls. create a new one.'))
