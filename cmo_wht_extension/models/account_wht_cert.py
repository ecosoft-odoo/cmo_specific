# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
    income_tax_form = fields.Selection(
        [('pnd1', 'PND1'),
         ('pnd3', 'PND3'),
         ('pnd53', 'PND53')],
    )

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
                fy = cert.period_id.fiscalyear_id.code
                cert.number = '%s%s-%s' % (tax_forms[cert.income_tax_form],
                                           fy, cert.sequence_display)
