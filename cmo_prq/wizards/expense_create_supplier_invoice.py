# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _inherit = 'expense.create.supplier.invoice'

    require_prq = fields.Boolean(
        string='Require PRQ',
        default=False,
    )

    @api.multi
    def _prepare_prq(self, expense):
        self.ensure_one()
        return {
            'type': 'expense',
            'expense_id': expense.expense_id.id,
            'invoice_id': expense.expense_id.invoice_id.id,
        }

    @api.multi
    def action_create_supplier_invoice(self):
        super(ExpenseCreateSupplierInvoice, self) \
            .action_create_supplier_invoice()
        Expense = self.env['hr.expense.line']
        expense = Expense.search(
            [('expense_id', '=', self._context.get('active_id', False))])
        if expense and self.require_prq:
            prepare_prq = self._prepare_prq(expense)
            prq = self.env['purchase.prq'].create(prepare_prq)
            prq.invoice_id.write({'prq_id': prq.id})
        return True
