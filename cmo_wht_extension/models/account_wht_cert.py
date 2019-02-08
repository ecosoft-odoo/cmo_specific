# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountWhtCert(models.Model):
    _inherit = 'account.wht.cert'

    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
    )
    expense_number = fields.Char(
        string='Expense',
        related='expense_id.number',
        readonly=True,
    )
    reference = fields.Char(
        string='Reference',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    additional_filing = fields.Boolean(
        string='Additional Filing',
        default=False,
        help="If this cert is marked as additional filing, user will manuall "
        "key in rpt_period",
    )
    rpt_period_id = fields.Many2one(
        'account.period',
        string='Reporting Period',
        help="By default, rpt_period_id is equal to period_id. But if "
        "additional filing is selected, user can choose this field manually",
        default=lambda self: self.env['account.period'].find(),
    )
    income_tax_form = fields.Selection(
        [('pnd1', 'PND1'),
         ('pnd3', 'PND3'),
         ('pnd53', 'PND53')],
    )
    # Overwrite, change period -> rpt_period_id
    _sql_constraints = [
        ('wht_seq_uunique',
         'unique (rpt_period_id, sequence, income_tax_form)',
         'WHT Sequence must be unique!'),
    ]

    @api.multi
    def _assign_wht_sequence(self):
        """ Overwrite """
        Period = self.env['account.period']
        for cert in self:
            if not cert.income_tax_form:
                raise ValidationError(_("No Income Tax Form selected, "
                                        "can not assign WHT Sequence"))
            if cert.sequence:
                continue
            period = Period.find(cert.date)[:1]
            cert.write({'period_id': period.id})
            # Change to using rpt_period_id for sequence
            sequence = cert._get_next_wht_sequence(cert.income_tax_form,
                                                   cert.rpt_period_id)
            cert.sequence = sequence

    @api.multi
    @api.depends('sequence')
    def _compute_wht_sequence_display(self):
        """ Overwrite, use rpt_period_id to replace period_id """
        for rec in self:
            if rec.period_id and rec.sequence:
                date_start = rec.rpt_period_id.date_start
                mo = datetime.strptime(date_start,
                                       '%Y-%m-%d').date().month
                month = '{:02d}'.format(mo)
                sequence = '{:04d}'.format(rec.sequence)
                rec.sequence_display = '%s/%s' % (month, sequence)

    @api.model
    def create(self, vals):
        rec = super(AccountWhtCert, self).create(vals)
        if 'additional_filing' in vals or 'period_id' in vals or \
                'rpt_period_id' in vals:
            if not rec.additional_filing and \
                    rec.period_id.id != vals.get('rpt_period_id'):
                rec.rpt_period_id = rec.period_id
        return rec

    @api.multi
    def write(self, vals):
        res = super(AccountWhtCert, self).write(vals)
        if 'additional_filing' in vals or 'period_id' in vals or \
                'rpt_period_id' in vals:
            for rec in self:
                if not rec.additional_filing and \
                        rec.period_id.id != vals.get('rpt_period_id'):
                    rec.rpt_period_id = rec.period_id
        return res

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_validate(self):
        self.write({'state': 'done'})
        return True

    @api.model
    def default_get(self, fields):
        res = super(AccountWhtCert, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model is None:
            company_partner = self.env.user.company_id.partner_id
            res['company_partner_id'] = company_partner.id
        if active_model == 'hr.expense.expense':
            expense = self.env[active_model].browse(active_id)
            company_partner = self.env.user.company_id.partner_id
            supplier = expense.employee_id.user_id.partner_id
            res['expense_id'] = expense.id
            res['date'] = expense.date
            res['company_partner_id'] = company_partner.id
            res['supplier_partner_id'] = supplier.id
        return res

    @api.multi
    def _assign_number(self):
        """ PND1: XSCMYY, PND3: XPCMYY, PND53: XCCMYY """
        tax_forms = {'pnd1': 'XSCM',
                     'pnd3': 'XPCM',
                     'pnd53': 'XCCM'}
        super(AccountWhtCert, self)._assign_number()
        for cert in self:
            if cert.sequence:
                fy = cert.rpt_period_id.fiscalyear_id.code
                cert.number = '%s%s-%s' % (tax_forms[cert.income_tax_form],
                                           fy, cert.sequence_display)

    def init(self, cr):
        cr.execute("""
            update account_wht_cert set rpt_period_id = period_id
            where rpt_period_id is null and period_id is not null
        """)
