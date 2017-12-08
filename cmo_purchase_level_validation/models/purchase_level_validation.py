# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    level_id = fields.Many2one(
        'level.validation',
        string='Validation Level',
        track_visibility='onchange',
        copy=False,
    )
    approver_ids = fields.Many2many(
        'res.users',
        'purchase_approver_rel', 'purchase_id', 'user_id',
        string='Approval',
        track_visibility='onchange',
        copy=False,
    )
    approve_permission = fields.Boolean(
        string='Approve Permission',
        compute='_compute_approve_permission',
    )

    @api.multi
    def action_check_approval(self):
        self.ensure_one()
        amount_untaxed = self.amount_untaxed
        levels = self.env['level.validation'].search([
            ('operating_unit_id', '=', self.operating_unit_id.id),
            ('doctype', 'like', 'purchase_order'),
        ]).sorted(key=lambda r: r.level)
        if not levels:
            raise ValidationError(_("This operating unit does not "
                                    "set approver."))
        levels_lt_amount = levels.filtered(
            lambda r: r.limit_amount < amount_untaxed)
        levels_gt_amount = levels.filtered(
            lambda r: r.limit_amount >= amount_untaxed)
        if levels_gt_amount:
            target_levels = levels_lt_amount + levels.filtered(
                lambda r: r.level == min(levels_gt_amount.mapped('level')))
        else:
            target_levels = levels_lt_amount
            if not target_levels.filtered(
                    lambda r: r.limit_amount >= amount_untaxed):
                raise ValidationError(_("Amount Untaxed is over "
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
            order.approve_permission = self.env.user in order.approver_ids
