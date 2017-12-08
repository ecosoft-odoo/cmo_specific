# -*- coding: utf-8 -*-
from openerp import models, fields, tools


class StockHistory(models.Model):
    _inherit = 'stock.history'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )

    # Replace
    def init(self, cr):
        """
            This function is overide the core module (stock_history)
            which view will show additional 3 fields composed of
                1. picking_name or source
                2. partner_id or supplier_id
                3. operating_unit_id (stock_picking, purchase_order)
        """
        tools.drop_view_if_exists(cr, 'stock_history')
        cr.execute("""
            CREATE OR REPLACE VIEW stock_history AS (
              SELECT MIN(id) as id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                SUM(quantity) as quantity,
                date,
                COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
                case when source is null then picking_name else source end as source,
                case when source is null then partner_id else supplier_id end as partner_id,
                case when source is null then sp_operating_unit_id else po_operating_unit_id end as operating_unit_id
                FROM
                ((SELECT
                    stock_move.id AS id,
                    stock_move.id AS move_id,
                    dest_location.id AS location_id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_picking.name AS picking_name,
                    purchase_order.partner_id AS supplier_id,
                    stock_picking.partner_id AS partner_id,
                    purchase_order.operating_unit_id AS po_operating_unit_id,
                    stock_picking.operating_unit_id AS sp_operating_unit_id
                FROM
                    stock_move
                JOIN
                    stock_quant_move_rel on stock_quant_move_rel.move_id = stock_move.id
                JOIN
                    stock_quant as quant on stock_quant_move_rel.quant_id = quant.id
                JOIN
                   stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                FULL OUTER JOIN
                    stock_picking ON stock_move.picking_id = stock_picking.id
                FULL OUTER JOIN
                    purchase_order ON stock_move.origin = purchase_order.name
                WHERE quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit')
                  AND (
                    not (source_location.company_id is null and dest_location.company_id is null) or
                    source_location.company_id != dest_location.company_id or
                    source_location.usage not in ('internal', 'transit'))
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.categ_id AS product_categ_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_picking.name AS picking_name,
                    purchase_order.partner_id AS supplier_id,
                    stock_picking.partner_id AS partner_id,
                    purchase_order.operating_unit_id AS po_operating_unit_id,
                    stock_picking.operating_unit_id AS sp_operating_unit_id
                FROM
                    stock_move
                JOIN
                    stock_quant_move_rel on stock_quant_move_rel.move_id = stock_move.id
                JOIN
                    stock_quant as quant on stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                FULL OUTER JOIN
                    stock_picking ON stock_move.picking_id = stock_picking.id
                FULL OUTER JOIN
                    purchase_order ON stock_move.origin = purchase_order.name
                WHERE quant.qty>0 AND stock_move.state = 'done' AND source_location.usage in ('internal', 'transit')
                 AND (
                    not (dest_location.company_id is null and source_location.company_id is null) or
                    dest_location.company_id != source_location.company_id or
                    dest_location.usage not in ('internal', 'transit'))
                ))
                AS foo
                GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, source, picking_name, supplier_id, partner_id, po_operating_unit_id, sp_operating_unit_id
            )""")
