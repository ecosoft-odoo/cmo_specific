# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    number = fields.Char(
        string='Asset Code',
        copy=False,
    )
    purchase_date = fields.Date(
        string='Purchase Date',
        required=False,
        copy=False,
    )
    purchase_move_id = fields.Many2one(
        'account.move',
        string='Purchase Move',
        readonly=True,
    )
    value_net_book = fields.Float(
        string='Net Book Value',
        compute='_compute_value_net_book',
        help='calculate from (purchase value - depreciated value)',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        readonly=True,
        default=lambda self:
            self.env['res.users'].operating_unit_default_get(self._uid)
    )
    asset_brand = fields.Char(
        string='Brand',
    )
    asset_model = fields.Char(
        string='Model',
    )
    serial_number = fields.Char(
        string='Serial Number',
    )
    warranty_number = fields.Char(
        string='Warranty Number',
    )
    warranty_start_date = fields.Date(
        string='Warranty Start Date',
    )
    warranty_expire_date = fields.Date(
        string='Warranty Expire Date',
    )
    tangible_asset = fields.Boolean(
        default=False,
        string='Tangible Asset',
    )
    transportation_expense = fields.Float(
        string='Transportation Expense',
    )
    installation_expense = fields.Float(
        string='Installation Expense',
    )
    other_expense = fields.Float(
        string='Other Expense',
    )
    insurance_company = fields.Char(
        string='Insurance Company',
    )
    premium = fields.Float(
        string='Premium',
    )
    sale_value = fields.Float(
        string='Sale Value',
    )
    voucher_number = fields.Char(
        compute='_compute_voucher_number',
        string='Voucher Number',
    )
    accum_depre_bf = fields.Float(
        string='Accum. Depre. B/F',
    )
    customer_invoice_number = fields.Char(
        string='Customer Invoice Number',
        readonly=True,
    )

    @api.multi
    def _compute_voucher_number(self):
        for rec in self:
            if rec.purchase_move_id:
                imove_lines = rec.mapped('purchase_move_id').line_id
                pmove_lines = imove_lines.mapped('reconcile_id').\
                    line_id.filtered(lambda l: l not in imove_lines)
                if pmove_lines:
                    rec.voucher_number = pmove_lines[-1].move_id.name

    @api.multi
    def _compute_value_net_book(self):
        for rec in self:
            rec.value_net_book = rec.purchase_value - rec.value_depreciated

    @api.model
    def _get_depreciation_entry_name(self, seq):
        """ change from code to number """
        return (self.number or str(self.id)) + '/' + str(seq)

    @api.multi
    def validate(self):
        for asset in self:
            if not asset.number:
                if asset.profile_id:
                    number = self.env['ir.sequence'].get_id(
                        asset.profile_id.sequence_id.id)
                    asset.write({
                        'number': number,
                    })
                else:
                    raise ValidationError(_('Asset Profile must be selected.'))
        return super(AccountAsset, self).validate()

    @api.multi
    def close(self):
        for asset in self:
            if asset.value_depreciated:
                raise ValidationError(_(
                    'Can not close! Depreciated value is not equal 0.'))
            asset.state = 'close'
        return True

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.code and record.code != '/':
                name = "[%s] %s" % (record.code, record.name)
            else:
                name = record.name
            res.append((record.id, name))
        return res

    @api.multi
    def create_depre_init_entry_on_migration(self):
        """ This function is used for migrated data only.
        It will create depre JE for the second line (type = depre, init = true)
        only if it is not created before (one time only)
        """
        DepreLine = self.env['account.asset.line']
        for asset in self:
            depre_line = DepreLine.search([('type', '=', 'depreciate'),
                                           ('init_entry', '=', True),
                                           ('move_check', '=', False),
                                           ('asset_id', '=', asset.id)])
            depre_line.create_move()
        return True

    # @api.model
    # def create(self, vals):
    #     if vals.get('number', '/') == '/':
    #         if vals.get('profile_id'):
    #             profile_id = self.env['account.asset.profile'].browse(
    #                 vals.get('profile_id'))
    #             vals['number'] = self.env['ir.sequence'].get_id(
    #                 profile_id.sequence_id.id)
    #         else:
    #             raise ValidationError(_('Asset Profile must be selected.'))
    #     res = super(AccountAsset, self).create(vals)
    #     return res
