# -*- coding: utf-8 -*-
from copy import deepcopy

from openerp import models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_round


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice,
                           self).finalize_invoice_move_lines(move_lines)
        new_move_lines = []

        for line_tuple in move_lines:
            if line_tuple[2].get('asset_profile_id', False) and \
                    line_tuple[2].get('quantity', False):
                quantity = line_tuple[2]['quantity']
                if quantity is False:
                    raise ValidationError(_('Please insert asset quantity.'))
                if not float(quantity).is_integer():
                    raise ValidationError(_("Asset Quantity must be integer."))
                if quantity <= 0.0:
                    raise ValidationError(
                        _("Asset Quantity must more than zero."))

                if quantity == 1.0:
                    new_move_lines.append(line_tuple)
                else:
                    price_unit = float_round(
                        line_tuple[2]['debit'] / quantity, 2)
                    last_price = line_tuple[2]['debit']
                    for i in range(int(quantity)):
                        new_line_tuple = deepcopy(line_tuple)  # copy tuple
                        new_line_tuple[2]['quantity'] = 1.0
                        if i == int(quantity) - 1:
                            new_line_tuple[2]['debit'] = last_price
                        else:
                            new_line_tuple[2]['debit'] = price_unit
                        new_move_lines.append(new_line_tuple)
                        last_price = float_round(last_price - price_unit, 2)
            else:
                new_move_lines.append(line_tuple)
        return new_move_lines


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.constrains('quantity')
    def _constraints_invoice_line_with_asset(self):
        for line in self:
            if line.asset_profile_id and line.quantity:
                quantity = float(line.quantity)
                if quantity is False:
                    raise ValidationError(_('Please insert asset quantity.'))
                if not quantity.is_integer():
                    raise ValidationError(_("Asset Quantity must be integer."))
                if quantity <= 0.0:
                    raise ValidationError(
                        _("Asset Quantity must more than zero."))
