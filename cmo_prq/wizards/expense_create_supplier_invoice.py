# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _inherit = 'expense.create.supplier.invoice'

    require_prq = fields.Boolean(
        string='Require PRQ',
    )

    @api.multi
    def _prepare_prq(self, expense):
        self.ensure_one()
        return {
            'type': 'expense',
            'expense_id': expense.id,
            'invoice_id': expense.invoice_id.id,
        }

    @api.multi
    def action_create_supplier_invoice(self):
        res = super(ExpenseCreateSupplierInvoice, self) \
            .action_create_supplier_invoice()
        expense_id = self._context.get('active_id', False)
        if expense_id:
            expense = self.env['hr.expense.expense'].browse(expense_id)
            if self.require_prq:
                prq_dict = self._prepare_prq(expense)
                prq = self.env['purchase.prq'].create(prq_dict)
                expense.invoice_id.write({'prq_id': prq.id})
            expense.write({'require_prq': self.require_prq})
        return res
