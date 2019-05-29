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
                                                    'purchase_order')
                    # --
                    self.write({
                        'level_id': target_level_id,
                        'approver_ids': [
                            (6, 0, approver_ids)
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

                    target_level_id, approver_ids = \
                        self._finalize_target_level(target_level,
                                                    self.operating_unit_id,
                                                    'purchase_order')

                    self.write({
                        'level_id': target_level_id,
                        'approver_ids': [
                            (6, 0, approver_ids)
                        ],
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
        requester = self.create_uid
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
            order.approve_permission = self.env.user in order.approver_ids

    @api.multi
    def action_cancel_draft(self):
        res = super(PurchaseOrder, self).action_cancel_draft()
        self._check_extra_permission(type="set to draft")
        return res

    @api.multi
    def wkf_action_cancel(self):
        super(PurchaseOrder, self).wkf_action_cancel()
        self._check_extra_permission(type="force cancel")

    @api.multi
    def action_cancel(self):
        res = super(PurchaseOrder, self).action_cancel()
        self._check_extra_permission(type="cancel")
        return res

    @api.multi
    def _check_extra_permission(self, type=""):
        """
        This method check for user's permission in managing document.
        """
        self.ensure_one()
        OperatingUnit = self.env['operating.unit']
        operating_units = OperatingUnit.search(
            [('name', '=', 'Internal Audit')])
        default_operating_unit = self.env.user.default_operating_unit_id
        # Check that user is internal audit
        if default_operating_unit.id in operating_units.ids:
            # The user has not permission in all doc except their doc
            if self.operating_unit_id != default_operating_unit:
                raise ValidationError(
                    _("You are not allowed %s this document "
                      "with difference OU." % (type)))
