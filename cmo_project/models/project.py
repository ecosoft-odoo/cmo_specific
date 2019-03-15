# -*- coding: utf-8 -*-
# from lxml import etree
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare

# TODO: foreign key use, idex and ondelete


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _order = "date_start desc"

    code = fields.Char(
        related='analytic_account_id.code',
        store=True,
        help="For project.project, no default, and do sequence when created"
    )
    use_tasks = fields.Boolean(
        default=False,
    )
    project_place = fields.Char(
        string='Project Place',
        states={'close': [('readonly', True)]},
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        states={'close': [('readonly', True)]},
        domain=[('customer', '=', True), ('brand_type_id', '!=', 'Employee')],
        required=True,
    )
    agency_partner_id = fields.Many2one(
        'res.partner',
        string='Agency',
        states={'close': [('readonly', True)]},
        domain=[('category_id', 'like', 'Agency'), ],
    )
    brand_type_id = fields.Many2one(
        'project.brand.type',
        string='Brand type',
        related='partner_id.brand_type_id',
        readonly=True,
        store=True,
    )
    industry_id = fields.Many2one(
        'project.industry',
        string='Industry',
        related='partner_id.industry_id',
        readonly=True,
        store=True,
    )
    client_type_id = fields.Many2one(
        'project.client.type',
        string='Client Type',
        states={'close': [('readonly', True)]},
    )
    obligation_id = fields.Many2one(
        'project.obligation',
        string='Obligation',
        states={'close': [('readonly', True)]},
    )
    function_id = fields.Many2one(
        'project.function',
        string='Function',
        states={'close': [('readonly', True)]},
    )
    location_id = fields.Many2one(
        'project.location',
        string='Location',
        states={'close': [('readonly', True)]},
    )
    description = fields.Text(
        string='Description',
        states={'close': [('readonly', True)]},
    )
    project_from_id = fields.Many2one(
        'project.from',
        string='Project From',
        states={'close': [('readonly', True)]},
    )
    project_type_id = fields.Many2one(
        'project.type',
        string='Project Type',
        states={'close': [('readonly', True)]},
    )
    project_budget = fields.Float(
        string='Project Budget',
        states={'close': [('readonly', True)]},
    )
    actual_price = fields.Float(
        string='Actual Price',
        states={'close': [('readonly', True)]},
        compute='_compute_price_and_cost',
        store=True,
        help="Sum of untaxed amount Quotation.",
    )
    estimate_cost = fields.Float(
        string='Estimate Cost',
        states={'close': [('readonly', True)]},
        compute='_compute_price_and_cost',
        store=True,
        help="Sum of untaxed amount estimated unit cost on Quotation.",
    )
    pre_cost = fields.Float(
        string='Pre-Project',
        states={'close': [('readonly', True)]},
    )
    actual_po = fields.Float(
        string='Actual PO',
        states={'close': [('readonly', True)]},
        compute='_compute_actual_po',
        store=True,
        help="Sum of untaxed amount on Purchase Order.",
    )
    remain_advance = fields.Float(
        string='Advance Balance',
        compute='_compute_remain_advance',
        states={'close': [('readonly', True)]},
        help="Sum of amount to clearing related project.",
    )
    expense = fields.Float(
        string='Expense',
        states={'close': [('readonly', True)]},
        compute='_compute_expense',
        store=True,
        help="Sum of untaxed amount on Expenses and Employee Clearing.",
    )
    date_brief = fields.Date(
        string='Brief Date',
        default=lambda self: fields.Date.context_today(self),
        states={'close': [('readonly', True)]},
    )
    date = fields.Date(
        string='End Date',
        default=lambda self: fields.Date.context_today(self),
        states={'close': [('readonly', True)]},
    )
    competitor_ids = fields.Many2many(
        'project.competitor',
        'res_competitor_rel', 'project_id', 'competitor_id',
        string='Competitors',
        states={'close': [('readonly', True)]},
    )
    project_member_ids = fields.One2many(
        'project.team.member',
        'project_id',
        string='Team Member',
        states={'close': [('readonly', True)]},
    )
    close_reason = fields.Selection(
        [('close', 'Completed'),
         ('it_close', 'IT Close Project'),
         ('reject', 'Reject'),
         ('lost', 'Lost'),
         ('cancel', 'Cancelled'),
         ('terminate', 'Terminated'), ],
        string='Close Reason',
        states={'close': [('readonly', True)]},
    )
    department_id = fields.Many2one(  # no use
        'hr.department',
        string='Department',
        states={'close': [('readonly', True)]},
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        default=lambda self: self.env.user.default_operating_unit_id,
        states={'close': [('readonly', True)]},
    )
    state = fields.Selection(
        [('template', 'Template'),
         ('draft', 'Draft'),
         ('validate', 'Validated'),
         ('open', 'In Progress'),
         ('ready_billing', 'Ready to Billing'),
         ('invoiced', 'Invoiced'),   # no use state invoiced and paid
         ('paid', 'Paid'),  # no use state invoiced and paid
         ('cancelled', 'Incompleted'),
         ('pending', 'Hold'),
         ('close', 'Completed'), ],
        string='Status',
        # track_visibility='onchange',
        required=True,
        copy=False,
        default='draft',
        compute='_compute_is_invoiced_and_paid',
        store=True,
    )
    state_before_inactive = fields.Char(
        string='Latest State',
    )
    is_active_state = fields.Boolean(
        string='Is Active State',
        compute='_get_state_before_inactive',
    )
    lost_reason_id = fields.Many2one(
        'project.lost.reason',
        string='Lost Reason',
    )
    lost_by_id = fields.Many2one(
        'project.competitor',
        string='Lost By',
    )
    reject_reason_id = fields.Many2one(
        'project.reject.reason',
        string='Reject Reason',
    )
    hold_reason = fields.Text(
        string='Hold Reason',
        states={'close': [('readonly', True)]},
    )
    assign_id = fields.Many2one(
        'res.users',
        string='Assign to',
        states={'close': [('readonly', True)]},
    )
    assign_description = fields.Text(
        string='Description',
        states={'close': [('readonly', True)]},
    )
    project_parent_id = fields.Many2one(
        'project.project',
        string='Parent Project',
        states={'close': [('readonly', True)]},
        store=True,
    )
    quote_related_ids = fields.One2many(
        'sale.order',
        'project_related_id',
        string='Related Quotation',
        domain=[('order_type', '=', 'quotation'), ],
    )
    sale_order_related_ids = fields.One2many(
        'sale.order',
        'project_related_id',
        string='Related Sale Order',
        domain=[('order_type', '=', 'sale_order'), ],
    )
    quote_related_count = fields.Integer(
        string='# of Quotation',
        compute='_compute_quote_related_count',
    )
    purchase_related_ids = fields.One2many(
        'purchase.order',
        'project_id',
        string='Related Project',
    )
    purchase_related_count = fields.Integer(
        string='# of Purchase',
        compute='_compute_purchase_related_count',
    )
    expense_related_count = fields.Integer(
        string='# of Expense',
        compute='_compute_expense_related_count',
    )
    remaining_cost = fields.Float(
        string='Remaining Cost',
        compute='_compute_remaining_cost',
        help="(estimated cost + pre-project) - (actual PO + expense)",
    )
    out_invoice_ids = fields.One2many(
        'account.invoice',
        'project_ref_id',
        string='Related Invoice',
        domain=[('type', '=', 'out_invoice'), ],
    )
    out_invoice_count = fields.Integer(
        string='# of Out Invoice',
        compute='_compute_out_invoice_count',
    )
    is_invoiced = fields.Boolean(
        string='Invoiced',
        compute='_compute_is_invoiced_and_paid',
        store=True,
        help="Triggered when at least 1 invoice is opened",
    )
    is_paid = fields.Boolean(
        string='Paid',
        compute='_compute_is_invoiced_and_paid',
        store=True,
        help="Triggered when at all sale order are done and cancel",
    )
    adjustment_ids = fields.One2many(
        'project.adjustment',
        'project_id',
        string='Adjustment Description',
    )
    adjustment_amount = fields.Float(
        string='Adjustment',
        compute='_compute_adjustment_amount',
    )

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form',
    #                     toolbar=False, submenu=False):
    #     res = super(ProjectProject, self).fields_view_get(
    #         view_id, view_type, toolbar=toolbar, submenu=submenu)
    #
    #   readonly_group = self.env.ref('project.group_project_readonly')
    #   readonly_group_own = self.env.ref('project.group_project_readonly_own')
    #     user = self.env['res.users'].search([
    #         ('id', '=', self._context.get('uid')),
    #     ])
    #     meet_user = (user in readonly_group.users) or \
    #         (user in readonly_group_own.users)
    #
    #     if meet_user and user.id != 1:
    #         root = etree.fromstring(res['arch'])
    #         root.set('edit', 'false')
    #         res['arch'] = etree.tostring(root)
    #     return res

    @api.multi
    @api.depends('adjustment_ids')
    def _compute_adjustment_amount(self):
        for project in self:
            domain = [
                ('project_id', '=', project.id),
            ]
            amount = sum(self.env['project.adjustment'].sudo().search(
                domain).mapped('amount'))
            project.adjustment_amount = amount

    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        res = super(ProjectProject, self).copy(defaults)
        res._write({'state': 'draft'})
        return res

    @api.multi
    @api.depends('out_invoice_ids',
                 'out_invoice_ids.state',
                 'sale_order_related_ids.state',
                 'state')
    def _compute_is_invoiced_and_paid(self):
        for project in self:
            invoice_states = project.out_invoice_ids.mapped('state')
            sale_order_states = []

            for quote in project.quote_related_ids:
                domain = [
                    ('quote_id', '=', quote.id),
                    ('order_type', '=', 'sale_order'),
                ]
                sale_order_states = \
                    sale_order_states + \
                    self.env['sale.order'].sudo().\
                    search(domain).mapped('state')
            sale_order_states = list(set(sale_order_states))
            if 'open' in invoice_states or 'paid' in invoice_states:
                project.is_invoiced = True
            else:
                project.is_invoiced = False

            if ['done'] == sale_order_states or \
                    ['cancel'] in sale_order_states or \
                    ['done', 'cancel'] in sale_order_states:
                project.is_paid = True
            else:
                project.is_paid = False

            if project.is_invoiced and project.is_paid:
                project.state = 'close'
            else:
                if not project.state_before_inactive:
                    project.state = 'draft'
                else:
                    project.state = project.state_before_inactive

    @api.multi
    def action_validate(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Validated" % state_now)
        res = self.write({'state': 'validate'})
        return res

    @api.multi
    def action_approve(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; In Progress" % state_now)

        res = self.write({'state': 'open'})
        return res

    @api.multi
    def action_back_to_draft(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Draft" % state_now)
        res = self.write({'state': 'draft'})
        return res

    @api.multi
    def action_invoices(self):  # no use state invoiced and paid
        res = self.write({'state': 'invoiced'})
        return res

    @api.multi
    def action_received(self):  # no use state invoiced and paid
        res = self.write({'state': 'paid'})
        return res

    @api.multi
    def action_ready_billing(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Ready to Billing" % state_now)
        res = self.write({'state': 'ready_billing'})
        return res

    @api.multi
    def action_back_to_open(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; In Progress" % state_now)

        res = self.write({'state': 'open'})
        return res

    @api.multi
    def action_complete(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Completed" % state_now)
        res = self.write({'state': 'close'})
        return res

    @api.multi
    def set_done(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Completed" % state_now)
        return super(ProjectProject, self).set_done()

    @api.multi
    def set_pending(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Hold" % state_now)
        return super(ProjectProject, self).set_pending()

    @api.multi
    def set_cancel(self):
        state_now = dict(self.env["project.project"]._columns
                         ["state"].selection)[self.state]
        self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
            %s &#8594; Incompleted" % state_now)
        res = super(ProjectProject, self).set_cancel()
        draft_invoices = self.out_invoice_ids.sudo().filtered(
            lambda r: r.state == 'draft'
        )
        if draft_invoices:
            draft_invoices.sudo().write({'state': 'cancel'})
        return res

    @api.multi
    def action_released(self):
        if self.state_before_inactive:  # state_bf_hold
            state_now = dict(self.env["project.project"]._columns
                             ["state"].selection)[self.state]
            state_before = \
                dict(self.env["project.project"]._columns
                     ["state"].selection)[self.state_before_inactive]
            self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
                %s &#8594; %s" % (state_now, state_before))
            res = self.write({'state': self.state_before_inactive})
        else:
            state_now = dict(self.env["project.project"]._columns
                             ["state"].selection)[self.state]
            self.message_post(body="&emsp;&nbsp;&#8226; <b>Status</b> \
                %s &#8594; In Progress" % state_now)
            res = self.write({'state': 'open'})
        self.write({
            'close_reason': False,
            'lost_reason_id': False,
            'lost_by_id': False,
            'reject_reason_id': False,
        })
        return res

    @api.multi
    def _get_state_before_inactive(self):
        for project in self:
            if project.state and \
                    (project.state != 'pending') and \
                    (project.state != 'close') and \
                    (project.state != 'cancelled'):
                project.sudo().write({'state_before_inactive': project.state})

    @api.onchange('project_parent_id')
    def _onchange_project_parent_id(self):
        for project in self:
            parent_project = self.env['project.project'].browse(
                project.project_parent_id.id)
            project.parent_id = parent_project.analytic_account_id

    @api.multi
    @api.constrains('date_brief', 'date')
    def _check_date_briefs(self):
        self.ensure_one()
        if self.date_brief > self.date:
            return ValidationError("project brief-date must be lower "
                                   "than project end-date.")

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        self.ensure_one()
        count_project = self.env['project.project'].search_count(
                        [('name', '=', self.name)])
        if count_project > 1:
            raise ValidationError(_('Project name is duplicate.'))

    @api.multi
    def purchase_relate_project_tree_view(self):
        self.ensure_one()
        domain = [
            ('project_id', 'like', self.id),
        ]
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]
        result.update({'domain': domain})
        return result

    @api.multi
    @api.depends('purchase_related_ids')
    def _compute_purchase_related_count(self):
        for project in self:
            purchase_ids = self.env['purchase.order'].sudo().search([
                ('project_id', 'like', project.id),
            ])
            project.purchase_related_count = len(purchase_ids)

    @api.multi
    def invoice_relate_project_tree_view(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        result.update({'domain': [('id', 'in', self.out_invoice_ids.ids)]})
        return result

    @api.multi
    @api.depends('out_invoice_ids')
    def _compute_out_invoice_count(self):
        for project in self:
            invoice_ids = self.env['account.invoice'].sudo().search([
                ('id', 'in', project.out_invoice_ids.ids)
            ])
            project.out_invoice_count = len(invoice_ids)

    @api.multi
    def expense_relate_project_tree_view(self):
        self.ensure_one()
        ExpenseLine = self.env['hr.expense.line']
        Expense = self.env['hr.expense.expense']
        ex_lines = ExpenseLine.sudo().search([('analytic_account', '=',
                                               self.analytic_account_id.id)])
        expense_ids = ex_lines.mapped('expense_id').ids
        expenses = Expense.search([('id', 'in', expense_ids)])
        return {
            'name': _("Advances / Expenses"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.expense',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', expenses.ids)],
            'context': self._context,
            'nodestroy': True,
        }

    @api.multi
    def _compute_expense_related_count(self):
        ExpenseLine = self.env['hr.expense.line']
        Expense = self.env['hr.expense.expense']
        for project in self:
            ex_lines = ExpenseLine.sudo().search([
                ('analytic_account', '=', project.analytic_account_id.id)])
            expense_ids = ex_lines.mapped('expense_id').ids
            expenses = Expense.search([('id', 'in', expense_ids)])
            expenses = ex_lines.mapped('expense_id')
            project.expense_related_count = len(expenses)

    @api.multi
    @api.depends(
        'actual_price',
        'estimate_cost',
        'quote_related_ids',
        'quote_related_ids.order_line',
    )
    def _compute_price_and_cost(self):
        for project in self:
            actual_price = 0.0
            estimate_cost = 0.0
            quotes = project.sudo().quote_related_ids.filtered(
                lambda r: r.state in ('draft', 'done')
            )
            for quote in quotes:
                actual_price += quote.amount_untaxed
                estimate_cost += sum(quote.order_line.filtered(
                    lambda r: r.purchase_price > 0.0).mapped('purchase_price'))
            project.actual_price = actual_price
            project.estimate_cost = estimate_cost

    @api.multi
    @api.depends(
        'actual_po',
        'purchase_related_ids',
        'purchase_related_ids.state',
        'purchase_related_ids.amount_untaxed',
    )
    def _compute_actual_po(self):
        for project in self:
            purchase_orders = project.sudo().purchase_related_ids.filtered(
                lambda r: r.state in ('approved', 'done')
            )
            project.actual_po = sum(purchase_orders.mapped('amount_untaxed'))
        return True

    @api.multi
    @api.constrains('actual_po')
    def _check_actual_po(self):
        print self._context
        for project in self:
            if float_compare(project.remaining_cost, 0.0, 2) < 0:
                raise ValidationError(
                    _("Project %s, budget exceeded (%s)") %
                    (project.code, '{:,.2f}'.format(project.remaining_cost))
                )
        return True

    @api.multi
    def name_get(self):
        res = []
        for project in self:
            name = project.name or '/'
            if name and project.code:
                name = '[%s] %s' % (project.code, name)
            res.append((project.id, name))
        return res

    @api.multi
    @api.depends('estimate_cost', 'pre_cost', 'actual_po', 'expense')
    def _compute_remaining_cost(self):
        for project in self:
            remaining = \
                (project.sudo().estimate_cost + project.sudo().pre_cost) - \
                (project.sudo().actual_po + project.sudo().expense)
            project.remaining_cost = remaining

    @api.multi
    @api.depends('expense')
    def _compute_expense(self):
        for project in self:
            expense_lines = self.env['hr.expense.line'].sudo().search(
                [('analytic_account', '=', project.analytic_account_id.id)])
            expense = sum(expense_lines.filtered(
                lambda r: (r.expense_id.state in ('done', 'paid')) and
                          (r.expense_id.is_employee_advance is False)
                          ).mapped('amount_line_untaxed'))
            project.expense = expense

    @api.multi
    @api.depends('remain_advance')
    def _compute_remain_advance(self):
        for project in self:
            expense_lines = self.env['hr.expense.line'].sudo().search([
                ('analytic_account', '=', project.analytic_account_id.id),
            ])
            line_ids = expense_lines.filtered(
                lambda r: r.expense_id.is_employee_advance and
                (r.expense_id.state in 'paid'))
            project.remain_advance = sum(
                line_ids.mapped('expense_id').mapped('amount_to_clearing'))

    @api.multi
    def quotation_relate_project_tree_view(self):
        self.ensure_one()
        domain = [
            ('project_related_id', 'like', self.id),
            ('order_type', '=', 'quotation'),
        ]
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        result.update({'domain': domain})
        return result

    @api.multi
    @api.depends('quote_related_ids')
    def _compute_quote_related_count(self):
        for project in self:
            quote_ids = self.env['sale.order'].sudo().search([
                ('project_related_id', 'like', project.id),
                ('order_type', '=', 'quotation'),
            ])
            project.quote_related_count = len(quote_ids)

    @api.constrains('project_member_ids')
    def _check_date_start_end(self):
        for rec in self:
            for member_id in rec.project_member_ids.ids:
                member = self.env['project.team.member'].browse(member_id)
                if member.date_start > member.date_end:
                    raise ValidationError("team member start date must be "
                                          "lower than end date.")

    @api.multi
    def edit_project_adjustment(self):
        self.ensure_one()
        action = self.env.ref('cmo_project.action_project_adjustment')
        result = action.read()[0]
        dom = [('project_id', '=', self.id)]
        result.update({'domain': dom,
                       'context': {'default_project_id': self.id}})
        return result


class ProjectTeamMember(models.Model):
    _name = 'project.team.member'
    _description = 'Project Team Member'
    _rec_name = 'employee_id'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        ondelete='cascade',
        index=True,
    )
    position_id = fields.Many2one(
        'project.position',
        string='Member Position',
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Name',
        required=True,
    )
    date_start = fields.Date(
        string='Start',
    )
    date_end = fields.Date(
        string='End date',
    )
    remark = fields.Text(
        string="Remark"
    )


class ProjectBrandType(models.Model):
    _name = 'project.brand.type'
    _description = 'Project Brand Type'

    name = fields.Char(
        string='Brand Type',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Brand Type must be unique!'),
    ]


class ProjectClientType(models.Model):
    _name = 'project.client.type'
    _description = 'Project Client Type'

    name = fields.Char(
        string='Client Type',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Client Type must be unique!'),
    ]


class ProjectIndustry(models.Model):
    _name = 'project.industry'
    _description = 'Project Industry'

    name = fields.Char(
        string='Industry',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Industry must be unique!'),
    ]


class ProjectLocation(models.Model):
    _name = 'project.location'
    _description = 'Project Location'

    name = fields.Char(
        string='Location',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Location must be unique!'),
    ]


class ProjectObligation(models.Model):
    _name = 'project.obligation'
    _description = 'Project Obligation'

    name = fields.Char(
        string='Obligation',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Obligation must be unique!'),
    ]


class ProjectFrom(models.Model):
    _name = 'project.from'
    _description = 'Project From'

    name = fields.Char(
        string='Project From',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project From must be unique!'),
    ]


class ProjectFunction(models.Model):
    _name = 'project.function'
    _description = 'Project Function'

    name = fields.Char(
        string='Name',
        required=True,
        size=128,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Function must be unique!'),
    ]


class ProjectPosition(models.Model):
    _name = 'project.position'
    _description = 'Project Position'

    name = fields.Char(
        string='Position',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Position must be unique!'),
    ]


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Project Type'

    name = fields.Char(
        string='Project Type',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Position must be unique!'),
    ]


class ProjectCompetitor(models.Model):
    _name = 'project.competitor'
    _description = 'Project Competitor'
    _rec_name = 'company'

    name = fields.Char(
        string='Name',
    )
    company = fields.Char(
        string='Company',
        required=True,
    )
    remark = fields.Text(
        string='Remark',
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Lost by must be unique!'),
    ]


class ProjectLostReason(models.Model):
    _name = 'project.lost.reason'
    _description = 'Project Lost Reason'

    name = fields.Char(
        string='Reason',
        required=True,
    )


class ProjectRejectReason(models.Model):
    _name = 'project.reject.reason'
    _description = 'Project Reject Reason'

    name = fields.Char(
        string='Reason',
        required=True,
    )
