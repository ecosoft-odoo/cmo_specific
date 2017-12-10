# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    list_account_ids = fields.Many2many(
        'account.account',
        string='List of Accounts',
        compute='_compute_list_account_ids',
        readonly=True,
    )
    list_ou_ids = fields.Many2many(
        'operating.unit',
        string='List of OUs',
        compute='_compute_list_ou_ids',
        readonly=True,
    )
    list_project_ids = fields.Many2many(
        'project.project',
        string='List of Projects',
        compute='_compute_list_project_ids',
        readonly=True,
    )

    @api.multi
    def _compute_list_account_ids(self):
        for rec in self:
            rec.list_account_ids = self.env['account.account'].search([])

    @api.multi
    def _compute_list_ou_ids(self):
        for rec in self:
            rec.list_ou_ids = self.env['operating.unit'].search([])

    @api.multi
    def _compute_list_project_ids(self):
        for rec in self:
            rec.list_project_ids = self.env['project.project'].search([])
