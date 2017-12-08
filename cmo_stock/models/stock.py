# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_id = fields.Many2one(
        'res.partner',
        default=lambda self: self.env.user.partner_id,
    )
    default_operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Default Operating Unit',
        compute='_compute_default_operating_unit_id',
    )

    @api.multi
    @api.depends('partner_id')
    def _compute_default_operating_unit_id(self):
        for picking in self:
            User = self.env['res.users']
            picking.default_operating_unit_id = False
            if picking.partner_id:
                user = User.search([('partner_id', '=',
                                     picking.partner_id.id)])
                if user:
                    picking.default_operating_unit_id = \
                        user[0].default_operating_unit_id.id

    @api.multi
    def action_open_stock(self):
        # Get product_id in each line
        product_ids = []
        for picking in self:
            product_ids += picking.move_lines.mapped('product_id').ids

        action = self.env.ref('stock_account.action_history_tree')
        result = action.read()[0]
        dom = "[('product_id','in',[" + ','.join(map(str, product_ids)) + "])]"
        ctx = "{'search_default_group_by_location': True, \
                'search_default_group_by_product': True}"
        result.update({'domain': dom, 'context': ctx})
        return result


class StockMove(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one(
        'project.project',
        string='Project name',
        domain=lambda self: [
            ('operating_unit_id', 'in', self.env.user.operating_unit_ids.ids)],
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        default=lambda self: self._get_location_dest_id(),
    )

    @api.model
    def _get_location_dest_id(self):
        Location = self.env['stock.location']
        user = self.env.user
        ou_id = user.default_operating_unit_id.id or False
        location = False
        if ou_id:
            location = Location.search([('operating_unit_id', '=', ou_id)])
        return location and location[0].id or False

    # @api.multi
    # @api.onchange('product_id', 'location_id', 'location_dest_id',
    #               'picking_id.partner_id')
    # def onchange_product_id(self):
    #     for move in self:
    #         res = super(StockMove, move).onchange_product_id(
    #             move.product_id.id, move.location_id.id,
    #             move.location_dest_id.id, move.picking_id.partner_id.id
    #         )
    #         if res:
    #             res = res['value']
    #             move.name = res.get('name', False)
    #             move.product_uom = res.get('product_uom', False)
    #             move.product_uos = res.get('product_uos', False)
    #             move.product_uom_qty = res.get('product_uom_qty', False)
    #             move.product_uos_qty = res.get('product_uos_qty', False)
    #             move.location_id = res.get('location_id', False)
    #             move.location_dest_id = res.get('location_dest_id', False)

    @api.constrains('location_id', 'location_dest_id')
    def _constrains_location_dest_id(self):
        for rec in self:
            if rec.location_id == rec.location_dest_id:
                raise ValidationError(_("Source location and destination "
                                        "location should not be the same."))


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def action_picking_type_form(self):
        user = self.env.user
        domain = [(1, '=', 1)]
        if user.has_group('stock.group_stock_manager'):
            domain = ['|', ('code', '=', 'incoming'),
                      '|', ('code', '=', 'outgoing'),
                           ('code', '=', 'internal')]
        elif user.has_group('cmo_stock.group_stock_wh_user'):
            domain = ['|', ('code', '=', 'incoming'),
                           ('code', '=', 'outgoing')]
        elif user.has_group('stock.group_stock_user'):
            domain = [('code', '=', 'outgoing')]
        elif user.has_group('cmo_stock.group_stock_readonly'):
            domain = [('code', '=', 'outgoing')]

        action = self.env.ref('stock.action_picking_type_form')
        result = action.read()[0]
        result.update({'domain': domain})
        return result


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def _adjust_dest_location(self):
        cr = self.env.cr
        cr.execute("SELECT id, name, operating_unit_id FROM stock_warehouse")
        warehouse_ids = cr.dictfetchall()
        for res in warehouse_ids:
            location_production_id = self.env['stock.location'].search([
                ('usage', '=', 'production'),
                ('name', '=', res['name'])
            ]) or False
            picking_type_id = self.env['stock.picking.type'].search([
                ('name', '=', 'Delivery Orders'),
                ('warehouse_id', '=', res['id']),
            ]) or False

            if picking_type_id and location_production_id:
                picking_type_id[0].write({
                    'default_location_dest_id': location_production_id[0].id})
                source_location = picking_type_id[0].default_location_src_id \
                    or False
                if source_location and res['operating_unit_id']:
                    source_location.write(
                        {'operating_unit_id': res['operating_unit_id']})
        return True
