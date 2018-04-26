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
        selection=[
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('validate', 'Waiting Validate'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
        ],
    )

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
                min_level = min(filter(lambda r: r >= self.level_id.level,
                                       target_levels.mapped('level')))
                target_level = target_levels.filtered(
                    lambda r: r.level == min_level + 1)
                if target_level:
                    self.write({
                        'level_id': target_level.id,
                        'approver_ids': [
                            (6, 0, target_level.user_ids.ids)
                        ],
                    })
                else:
                    self.write({
                        'level_id': False,
                        'approver_ids': False,
                    })
            else:
                if not self.level_id and not self.approver_ids:
                    target_level = target_levels.filtered(
                        lambda r: r.level == min(target_levels.mapped('level'))
                    )
                    self.write({
                        'level_id': target_level.id,
                        'approver_ids': [
                            (6, 0, target_level.user_ids.ids)
                        ],
                    })
        return True

    @api.depends('approver_ids')
    def _compute_approve_permission(self):
        for order in self:
            order.approve_permission = \
                bool(self.env.user in order.approver_ids)

    @api.multi
    def action_validated(self):
        self.ensure_one()
        return self.write({'state': 'validate'})

    @api.multi
    def expense_accept(self):
        self.ensure_one()
        res = super(HrExpenseExpense, self).expense_accept()
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
