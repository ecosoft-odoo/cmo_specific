# -*- coding: utf-8 -*-
from lxml import etree
from openerp import fields, models, api
from openerp.exceptions import ValidationError
from openerp.tools import float_compare
from openerp.tools.translate import _


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    employee_request_id = fields.Many2one(
        'hr.employee',
        string='Employee Request',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
        default=lambda self: self.env.user.partner_id.employee_id,
    )
    request_date = fields.Date(
        string='Received Date',
        default=lambda self: fields.Date.context_today(self),
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    due_date = fields.Date(
        string='Due Date Clearing',
        default=lambda self: fields.Date.context_today(self),
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    payment_by = fields.Selection(
        selection=lambda self: self._get_payment_by_selection(),
        string='Payment By',
    )
    bank_transfer_ref = fields.Text(
        string='Bank Transfer Ref.',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    ac_payee_ref = fields.Text(
        string='A/C Payee Ref.',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)],
        },
    )
    employee_id = fields.Many2one(
        states={
            'draft': [('readonly', True)],
            'confirm': [('readonly', True)],
        },
    )
    supplier_text = fields.Char(
        string='Supplier Name',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    approve_by = fields.Many2one(
        'res.users',
        string='Approve By',
        readonly=True,
        copy=False,
    )
    approve_date = fields.Datetime(
        string='Approve Date',
        readonly=True,
        copy=False,
    )

    @api.onchange('payment_by')
    def _onchange_payment_by(self):
        self.bank_transfer_ref = False
        self.ac_payee_ref = False

    @api.multi
    @api.constrains('request_date', 'due_date')
    def _check_due_date(self):
        for rec in self:
            if rec.request_date > rec.due_date:
                raise ValidationError(
                    _('Request Date must be lower than Due Date.'))

    @api.onchange('line_ids', 'advance_expense_id')
    def _onchange_hr_line_analytic(self):
        advance = self.advance_expense_id
        if advance and advance.is_employee_advance:
            self.employee_request_id = advance.employee_request_id
            for line in self.line_ids:
                line.analytic_account = advance.line_ids.analytic_account

    @api.multi
    def expense_confirm(self):
        res = super(HrExpenseExpense, self).expense_confirm()
        self._check_expense_amount()
        return res

    @api.multi
    def _check_expense_amount(self):
        for expense in self:
            expense_lines = self.env['hr.expense.line'].search([
                ('expense_id', '=', expense.id),
            ])
            error_names = []
            for analytic_account in expense_lines.mapped('analytic_account'):
                project = self.env['project.project'].search([
                    ('analytic_account_id', '=', analytic_account.id),
                ], limit=1)
                amount_lines = sum(expense_lines.filtered(
                    lambda r: r.analytic_account == analytic_account
                ).mapped('amount_line_untaxed'))
                if project:
                    remaining_cost = project.remaining_cost or 0.0
                    if float_compare(amount_lines, remaining_cost, 2) > 0:
                        error_names.append(project.name)
            if error_names:
                raise ValidationError(
                    _("Amount over remaining "
                      "cost, please change amount in line with "
                      "project %s" % ', '.join(error_names))
                )

    @api.model
    def _prepare_inv_header(self, partner_id, expense):
        res = super(HrExpenseExpense, self)._prepare_inv_header(
            partner_id, expense)
        if expense.operating_unit_id:
            res['operating_unit_id'] = expense.operating_unit_id.id or False
        return res

    @api.model
    def _prepare_inv_line(self, account_id, exp_line):
        res = super(HrExpenseExpense, self)._prepare_inv_line(
            account_id, exp_line)
        if exp_line.analytic_account:
            res['account_analytic_id'] = exp_line.analytic_account.id or False
        return res

    @api.constrains('line_ids')
    def _constrains_expense_line(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_('Must have at least 1 line!'))
            if not rec.is_employee_advance:
                product_line = [x for x in rec.line_ids if not x.product_id]

                # Check produce line is null
                if product_line:
                    raise ValidationError(_('In line must be product.'))
            if rec.is_advance_clearing:
                # Employee Advance has 1 line only.
                project = rec.advance_expense_id.line_ids.analytic_account
                if project:
                    project_line = [x for x in rec.line_ids
                                    if x.analytic_account != project]
                    if project_line:
                        raise ValidationError(
                            _('Project line not match with %s.')
                            % (rec.advance_expense_id.number))

    @api.model
    def _get_payment_by_selection(self):
        context = self._context.copy()
        res = [('cash', 'Cash'),
               ('cashier_cheque', 'Cashier Cheque'),
               ('bank_transfer', 'Bank Transfer'),
               ('ac_payee', 'A/C Payee'), ]
        if context.get('default_pay_to', False) == 'pettycash':
            res = [('cash', 'Cash'), ]
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(HrExpenseExpense, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('active_model') == 'project.project':
            # Hide action
            if res.get('toolbar', {}).get('action'):
                res['toolbar']['action'] = []
            # Hide create, edit, delete button in expense
            doc = etree.XML(res['arch'])
            nodes = doc.xpath('/tree') + doc.xpath('/form')
            for node in nodes:
                node.set('create', 'false')
                node.set('edit', 'false')
                node.set('delete', 'false')
            res['arch'] = etree.tostring(doc)
        return res


class HrExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    amount_line_untaxed = fields.Float(
        string='Total Untaxed',
        compute='_compute_amount_line_untaxed',
        readonly=True,
    )
    is_advance_clearing = fields.Boolean(
        string='Is Clearing',
        related='expense_id.is_advance_clearing',
        default=lambda self: self._context.get('is_advance_clearing', False),
    )

    @api.model
    def create(self, vals):
        expense = self.env['hr.expense.expense'].\
            browse(vals['expense_id'])
        advance = expense.advance_expense_id
        if advance and advance.is_employee_advance:
            vals['analytic_account'] = advance.line_ids.analytic_account.id
        res = super(HrExpenseLine, self).create(vals)
        return res

    @api.multi
    @api.depends('amount_line_untaxed')
    def _compute_amount_line_untaxed(self):
        for line in self:
            line.amount_line_untaxed = line.unit_amount * line.unit_quantity
