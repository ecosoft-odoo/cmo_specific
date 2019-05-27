# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    level_id = fields.Many2one(
        'level.validation',
        string='Validation Level',
        track_visibility='onchange',
        copy=False,
    )
    approver_ids = fields.Many2many(
        'res.users',
        'hr_approver_rel',
        'expense_id', 'user_id',
        string='Approver',
        track_visibility='onchange',
        copy=False,
    )
    approve_permission = fields.Boolean(
        string='Approve Permission',
        compute='_compute_approve_permission',
    )
    state = fields.Selection(
        [
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('validate', 'Waiting Validate'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
        ],
    )
    validate_date = fields.Datetime(
        'Validate On',
        readonly=True,
        copy=False,
    )
    show_doc = fields.Boolean(
        'Show Document',
        copy=False,
    )

    @api.multi
    def expense_confirm(self):
        res = super(HrExpenseExpense, self).expense_confirm()
        if self.employee_id.user_id.id != self.env.user.id and not \
                self.env.user.has_group('base.group_erp_manager'):
            raise ValidationError(_("Not permission to sent this file."))
        return res

    @api.multi
    def action_check_approval(self):
        self.ensure_one()
        amount = self.amount
        doctype = ''
        if self.is_employee_advance:
            doctype = 'employee_advance'
        elif self.is_advance_clearing:
            doctype = 'employee_clearing'
        elif self.pay_to == 'pettycash':
            doctype = 'employee_pettycash'
        elif not self.is_advance_clearing and not self.is_employee_advance:
            doctype = 'employee_expense'

        levels = self.env['level.validation'].search([
            ('operating_unit_id', '=', self.operating_unit_id.id),
            ('doctype', 'like', doctype),
        ]).sorted(key=lambda r: r.level)

        if not levels:
            raise ValidationError(_("This operating unit does not "
                                    "set approver."))
        levels_lt_amount = levels.filtered(
            lambda r: r.limit_amount < amount)
        levels_gt_amount = levels.filtered(
            lambda r: r.limit_amount >= amount)

        if levels_gt_amount:
            target_levels = levels_lt_amount + levels.filtered(
                lambda r: r.level == min(levels_gt_amount.mapped('level')))
        else:
            target_levels = levels_lt_amount
            if not target_levels.filtered(
                    lambda r: r.limit_amount >= amount):
                raise ValidationError(_("Amount is over "
                                        "maximum limited amount."))

        if self.approver_ids and self.env.user not in self.approver_ids:
            raise ValidationError(_("Your user is not allow to "
                                    "approve this document."))
        if target_levels:
            if self.level_id:
                next_levels = filter(lambda r: r >= self.level_id.level,
                                     target_levels.mapped('level'))
                min_level = next_levels and min(next_levels) or 100  # no level
                target_level = target_levels.filtered(
                    lambda r: r.level == min_level + 1)
                if target_level:
                    # Finalize Level
                    target_level_id, approver_ids = \
                        self._finalize_target_level(target_level,
                                                    self.operating_unit_id,
                                                    doctype)
                    # --
                    self.write({
                        'level_id': target_level_id,
                        'approver_ids': [
                            (6, 0, approver_ids)
                        ],
                        'show_doc': True,
                    })
                else:
                    self.write({
                        'level_id': False,
                        'approver_ids': False,
                        'show_doc': True,
                    })
            else:
                if not self.level_id and not self.approver_ids:
                    target_level = target_levels.filtered(
                        lambda r: r.level == min(target_levels.mapped('level'))
                    )

                    target_level_id, approver_ids = \
                        self._finalize_target_level(target_level,
                                                    self.operating_unit_id,
                                                    doctype)

                    self.write({
                        'level_id': target_level_id,
                        'approver_ids': [
                            (6, 0, approver_ids)
                        ],
                        'show_doc': True,
                    })
        return True

    @api.multi
    def _finalize_target_level(self, target_level, ou, doctype):
        """ If this user same as approver, find the next available level
            If next level not found, go to CFO
            If CFO not found show warning
        """
        self.ensure_one()
        approver_ids = target_level.user_ids.ids
        target_level_id = target_level.id
        if not target_level:
            raise ValidationError(_('No target_level in _check_target_level'))
        requester = self.employee_id.user_id
        if requester in target_level.user_ids:
            next_target_level = self.env['level.validation'].search([
                ('operating_unit_id', '=', ou.id),
                ('doctype', 'like', doctype),
                ('level', '>', target_level.level),
                ('user_ids', 'not in', [requester.id]),
            ], order='level', limit=1)
            if next_target_level:
                target_level_id = next_target_level.id
                approver_ids = next_target_level.user_ids.ids
            else:  # No next level, find CFO
                cfo_user = self.env['res.users'].search([('name', '=', 'CFO')])
                if not cfo_user:
                    raise ValidationError(
                        _('No user "CFO" in system, please administrator'))
                approver_ids = [cfo_user.id]
                # Use max target level, so it will be the last
                max_target_level = self.env['level.validation'].search([
                    ('operating_unit_id', '=', ou.id),
                    ('doctype', 'like', doctype)
                ], order='level desc', limit=1)
                target_level_id = max_target_level.id
        return (target_level_id, approver_ids)

    @api.depends('approver_ids')
    def _compute_approve_permission(self):
        for order in self:
            order.approve_permission = \
                bool(self.env.user in order.approver_ids)

    @api.multi
    def action_validated(self):
        self.ensure_one()
        today = fields.Datetime.now()
        return self.write({'state': 'validate',
                           'approve_by': self.env.user.id,
                           'approve_date': today})

    @api.multi
    def expense_accept(self):
        self.ensure_one()
        res = super(HrExpenseExpense, self).expense_accept()
        today = fields.Datetime.now()
        self.write({'validate_date': today})
        product_lines = self.env['hr.expense.line'].search([
            ('expense_id', '=', self.id)
        ]).mapped('product_id')
        hr_categories = self.env['product.category'].search([('hr_product',
                                                              '=', True)])
        hr_products = product_lines.filtered(
            lambda r: r.categ_id in hr_categories
        )
        group_hr = self.env.ref('hr.group_validate_hr_product')
        if hr_products and self.env.user not in group_hr.users:
            raise ValidationError(
                _("You are not allowed to validate document with HR Product."))
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        # Update show doc is False only
        self._cr.execute("""
            update hr_expense_expense
            set show_doc = False
            where show_doc = True""")
        return super(HrExpenseExpense, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
