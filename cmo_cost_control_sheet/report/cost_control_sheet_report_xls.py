# -*- coding: utf-8 -*-
import logging
import xlwt
import os
from xlwt.Style import default_style
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import _render
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from datetime import datetime
from pytz import timezone

_logger = logging.getLogger(__name__)


class CostControlSheetReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(CostControlSheetReportXlsParser, self).__init__(
            cr, uid, name, context=context)
        project_obj = self.pool.get('project.project')
        self.context = context
        wl_ccs = project_obj._xls_cost_control_sheet_fields(cr, uid, context)
        tmpl_ccs_upd = project_obj._xls_cost_control_sheet_template(
            cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list_cost_control_sheet': wl_ccs,
            'template_update_cost_control_sheet': tmpl_ccs_upd,
            '_': _,
        })


class CostControlSheetReportXls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(CostControlSheetReportXls, self).__init__(
            name, table, rml, parser, header, store
        )

        # Cell Styles
        _xs = self.xls_styles
        # header

        # Report Column Headers format
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])

        # Type view Column format
        fill_blue = 'pattern: pattern solid, fore_color 27;'
        av_cell_format = _xs['bold'] + fill_blue + _xs['borders_all']
        self.av_cell_style = xlwt.easyxf(av_cell_format)
        self.av_cell_style_decimal = xlwt.easyxf(
            av_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # Type normal Column Data format
        an_cell_format = _xs['borders_all']
        self.an_cell_style = xlwt.easyxf(an_cell_format)
        self.an_cell_style_center = xlwt.easyxf(an_cell_format + _xs['center'])
        self.an_cell_style_date = xlwt.easyxf(
            an_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        self.an_cell_style_decimal = xlwt.easyxf(
            an_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # XLS Template
        self.cost_control_sheet_template = {
            'name': {
                'quote': [1, 0, 'text', _render("quote_description")],
                'custom_group': [1, 0, 'text', _render("custom_group_name")],
                'section': [1, 0, 'text', _render("section_name")],
                'order_line': [
                    1, 0, 'text', _render("order_line_description"),
                    None, self.an_cell_style_date],
            },
            'price_in_contract': {
                'quote': [1, 0, 'text', None],
                'custom_group': [1, 0, 'text', None],
                'section': [1, 0, 'text', None],
                'order_line': [
                    1, 0, 'number', _render("price_in_contract"),
                    None, self.an_cell_style_decimal],
            },
            'estimate_cost': {
                'quote': [1, 0, 'text', None],
                'custom_group': [1, 0, 'text', None],
                'section': [1, 0, 'text', None],
                'order_line': [
                    1, 0, 'number', _render("estimate_cost"),
                    None, self.an_cell_style_decimal],
            },
            'percent_margin': {
                'quote': [1, 0, 'text', None],
                'custom_group': [1, 0, 'text', None],
                'section': [1, 0, 'text', None],
                'order_line': [
                    1, 0, 'number', _render("percent_margin"),
                    None, self.an_cell_style_decimal],
            },
        }

    def xls_merge_row(self, ws, row_pos, row_data,
                      row_style=default_style, set_column_size=False):
        r = ws.row(row_pos)
        for col, size, spec in row_data:
            data = spec[4]
            formula = spec[5].get('formula') and \
                xlwt.Formula(spec[5]['formula']) or None
            style = spec[6] and spec[6] or row_style
            if not data:
                # if no data, use default values
                data = report_xls.xls_types_default[spec[3]]
            if size != 1:
                if formula:
                    ws.write_merge(
                        row_pos, row_pos + size - 1, col, col, data, style)
                else:
                    ws.write_merge(
                        row_pos, row_pos + size - 1, col, col, data, style)
            else:
                if formula:
                    ws.write(row_pos, col, formula, style)
                else:
                    spec[5]['write_cell_func'](r, col, data, style)
            if set_column_size:
                ws.col(col).width = spec[2] * 256
        return row_pos + size

    def _report_title(self, ws, _p, row_pos, _xs, title, index, offset=0,
                      merge=1):
        border_style = 'borders: left thin, right thin, top thin, bottom thin;'
        cell_style = xlwt.easyxf(
            _xs['center'] + border_style + 'font: bold true, height 220;')
        col_style = None
        if index == 0:
            col_style = xlwt.easyxf(
                'pattern: pattern solid, fore_colour black;')
        elif index == 3:
            col_style = xlwt.easyxf(
                _xs['center'] + border_style + 'font: bold true, height 360;')
        c_specs = []
        if index < 3:
            c_specs += [('logo', 1, 0, 'text', None)]
        c_specs += [
            ('report_name', merge, 0, 'text', title, None, col_style),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        return row_pos + offset

    def _report_header(self, ws, _p, row_pos, _xs, title, offset=0, merge=1):
        cell_style = xlwt.easyxf(
            _xs['right'] + 'font: color black, bold false, height 220;')
        c_specs = [
            ('report_name', merge, 0, 'text', title),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        return row_pos + offset

    def _report_column_header(self, ws, _p, row_pos, _xs, row_merge=1):
        cell_style = xlwt.easyxf(
            'align: vertical center, horizontal center;' + _xs['bold'] +
            _xs['borders_all'])
        parent_titles = [
            {
                'text': 'Description',
                'size': 60,
                'col_span': 1,
                'row_span': 2,
            },
            {
                'text': 'Price as in Contract',
                'size': 20,
                'col_span': 1,
                'row_span': 2,
            },
            {
                'text': 'Estimated Cost',
                'size': 20,
                'col_span': 1,
                'row_span': 2,
            },
            {
                'text': 'Amount',
                'size': 20,
                'col_span': 1,
                'row_span': 1,
            },
            {
                'text': 'Price as in P/O',
                'size': 20,
                'col_span': 2,
                'row_span': 1,
            },
            {
                'text': 'Note/Comments',
                'size': 20,
                'col_span': 1,
                'row_span': 2,
            },
            {
                'text': 'Amount Margin',
                'size': 20,
                'col_span': 1,
                'row_span': 2,
            },
            {
                'text': 'Gross Margin (in%)',
                'size': 20,
                'col_span': 1,
                'row_span': 2,
            },
        ]
        child_titles = [
            {
                'text': '(Contract vs Estimate)',
                'size': 20,
                'col_pos': 3,
            },
            {
                'text': 'P/O No.',
                'size': 20,
                'col_pos': 4,
            },
            {
                'text': 'Price',
                'size': 20,
                'col_pos': 5,
            },
        ]
        col_offset = 0
        for column_i, data in enumerate(parent_titles):
            column_i += col_offset
            ws.write_merge(
                row_pos, row_pos + data['row_span'] - 1,
                column_i, column_i + data['col_span'] - 1,
                data['text'], style=cell_style
            )
            ws.col(column_i).width = data['size'] * 256
            if data['col_span'] > 0:
                col_offset += data['col_span'] - 1

        for data in child_titles:
            ws.write(
                row_pos + row_merge, data['col_pos'],
                data['text'], style=cell_style)
            ws.col(data['col_pos']).width = data['size'] * 256
        return row_pos + row_merge + 1

    def _extra_sql_where(self, sale_order_line_ref_ids):
        where = "AND (active = true"
        if sale_order_line_ref_ids:
            if len(sale_order_line_ref_ids) == 1:
                where += " OR id = %s" % str(sale_order_line_ref_ids[0])
            else:
                where += " OR id IN %s" % str(tuple(sale_order_line_ref_ids))
        where += ")"
        return where

    def _ordering_order_line(self, ws, _p, row_pos, quote_id):
        cr = self.cr
        uid = self.uid
        context = self.context
        section_obj = self.pool.get('sale_layout.category')
        order_line_obj = self.pool.get('sale.order.line')
        order_obj = self.pool.get('sale.order')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        line_and_parent = []

        def _line_order_get(custom_groups=None, sale_order_line_ref_ids=None):
            line_get = []
            if custom_groups:
                cr.execute(
                    "SELECT sale_layout_cat_id, COUNT(id) "
                    "FROM sale_order_line "
                    "WHERE order_id = %s AND order_lines_group = 'before' %s"
                    "GROUP BY order_lines_group, sale_layout_cat_id "
                    "ORDER BY order_lines_group, sale_layout_cat_id"
                    % (quote_id.id,
                       self._extra_sql_where(sale_order_line_ref_ids)))
            else:
                cr.execute(
                    "SELECT sale_layout_cat_id, COUNT(id) "
                    "FROM sale_order_line "
                    "WHERE order_id = %s %s "
                    "GROUP BY order_lines_group, sale_layout_cat_id "
                    "ORDER BY order_lines_group, sale_layout_cat_id"
                    % (quote_id.id,
                       self._extra_sql_where(sale_order_line_ref_ids)))
            section_ids = [x[0] for x in cr.fetchall()]
            for section_id in section_ids:
                section_id = section_obj.browse(
                    cr, uid, section_id, context=context)
                order_line_ids = order_line_obj.browse(
                    cr, uid, order_line_obj.search(cr, uid, [
                        ('sale_layout_cat_id', '=', section_id.id),
                        ('order_id', '=', quote_id.id),
                        ('sale_layout_custom_group', '=', custom_groups),
                    ], context=context)).filtered(
                        lambda l: l.active is True or
                        l.id in sale_order_line_ref_ids).ids
                if order_line_ids:
                    line_get.append(('section', section_id))
                line_list = [('line', order_line_obj.browse(
                    cr, uid, x, context=context)) for x in order_line_ids]
                line_get += line_list
                if order_line_ids:
                    subtotal_section = {
                        'name': 'Total %s' % (section_id.name),
                    }
                    line_get += [('subtotal_section', subtotal_section)]
            return line_get

        quote_data = ('quote', quote_id)
        line_and_parent.append(quote_data)
        # Find sale order line as active is False
        purchase_order_line_ids = purchase_order_line_obj.search(
            cr, uid,
            [('order_id.order_ref', '=', quote_id.id),
             ('sale_order_line_ref_id.active', '=', False),
             ('order_id.state', 'in', ('approved', 'done'))], context=context)
        sale_order_line_ref_ids = purchase_order_line_obj.browse(
            cr, uid, purchase_order_line_ids, context=context) \
            .mapped('sale_order_line_ref_id.id')
        # Find sale order line is False
        purchase_order_line_ids = purchase_order_line_obj.search(
            cr, uid,
            [('order_id.order_ref', '=', quote_id.id),
             ('sale_order_line_ref_id', '=', False),
             ('order_id.state', 'in', ('approved', 'done'))])
        if purchase_order_line_ids:
            sale_layout_cat_id = self.pool.get('ir.model.data') \
                .get_object_reference(
                    cr, uid, 'base', 'sale_layout_category_other')[1]
            sale_order_line_ref_ids += order_line_obj.search(
                cr, uid, [('order_id', '=', quote_id.id),
                          ('active', '=', False),
                          ('sale_layout_cat_id', '=', sale_layout_cat_id)],
                context=context)
        cr.execute(
            "SELECT sale_layout_custom_group, COUNT(id)  FROM sale_order_line "
            "WHERE order_id = %s %s GROUP BY sale_layout_custom_group "
            "ORDER BY sale_layout_custom_group ASC"
            % (quote_id.id, self._extra_sql_where(sale_order_line_ref_ids)))
        custom_groups = [x[0] for x in cr.fetchall()]
        if len(custom_groups) > 1:
            for custom_group in custom_groups:
                line_and_parent.append(('custom_group', custom_group))
                line_and_parent += _line_order_get(
                    custom_groups=custom_group,
                    sale_order_line_ref_ids=sale_order_line_ref_ids)
                subtotal_custom_group = {
                    'name': 'Total %s' % (custom_group),
                }
                line_and_parent += \
                    [('subtotal_custom_group', subtotal_custom_group)]

        else:
            line_and_parent += _line_order_get(
                sale_order_line_ref_ids=sale_order_line_ref_ids)
        order = order_obj.browse(cr, uid, quote_id.id)
        line_and_parent += [('discount', order.amount_discount)]
        subtotal_quote = {
            'name': 'Total Quotation %s' % (quote_id.name),
        }
        line_and_parent += [('subtotal_quote', subtotal_quote)]
        return line_and_parent

    def _get_purchase_specs(self):
        """
        Column specs of purchase
        """
        c_specs = [
            ['purchase_number', 1, 0, 'text', None],
            ['purchase_price', 1, 0, 'text', None],
            ['purchase_note', 1, 0, 'text', None],
            ['amount_margin', 1, 0, 'text', None],
            ['gross_margin', 1, 0, 'text', None]
        ]
        return c_specs

    def _get_expense_specs(self, name=None, number=None,
                           price=['number', None, None], employee=None):
        """
        Column specs of expense
        """
        c_specs = [
            ['name', 1, 0, 'text', name],
            ['space_1', 1, 0, 'text', None],
            ['space_2', 1, 0, 'text', None],
            ['space_3', 1, 0, 'text', None],
            ['number', 1, 0, 'text', number],
            ['price', 1, 0, price[0], price[1], price[2]],
            ['employee', 1, 0, 'text', employee],
            ['space_4', 1, 0, 'text', None],
            ['space_5', 1, 0, 'text', None]
        ]
        return c_specs

    def _get_invoice_specs(self, name=None, number=None,
                           price=['number', None, None], customer=None):
        """
        Column specs of invoices
        """
        c_specs = [
            ['name', 1, 0, 'text', name],
            ['price', 1, 0, price[0], price[1], price[2]],
            ['space_1', 1, 0, 'text', None],
            ['space_2', 1, 0, 'text', None],
            ['number', 1, 0, 'text', number],
            ['space_3', 1, 0, 'text', None],
            ['customer', 1, 0, 'text', customer],
            ['space_4', 1, 0, 'text', None],
            ['space_5', 1, 0, 'text', None]
        ]
        return c_specs

    def _cost_control_sheet_report(self, _p, _xs, data, objects, wb):
        cr = self.cr
        uid = SUPERUSER_ID
        context = self.context

        wl_ccs = _p.wanted_list_cost_control_sheet
        template = self.cost_control_sheet_template
        project_obj = self.pool['project.project']
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        expense_line_obj = self.pool.get('hr.expense.line')
        invoice_line_obj = self.pool.get('account.invoice.line')
        project_id = project_obj.browse(
            cr, uid, data['project_id'], context=context)

        sheet_name = "Cost Control Sheet"
        ws = wb.add_sheet(sheet_name, cell_overwrite_ok=True)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.show_zero_values = False
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        ws.row(3).height = 450

        # Insert logo
        report_dir = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        ws.insert_bitmap(
            '%s/static/description/cmo.bmp' % report_dir, 0, 0, x=26.4, y=5,
            scale_x=0.08, scale_y=0.5)

        # Merge row of logo
        ws.write_merge(row_pos, 2, 0, 0)

        company_id = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        titles = [
            '',
            ' '.join([company_id.street, company_id.street2, company_id.zip,
                      company_id.country_id.name]) or '',
            'Tel: %s  Fax: %s  Website: %s  E-mail: %s ' % (
                company_id.phone or '-',
                company_id.fax or '-',
                company_id.website or '-',
                company_id.email or '-'
            ),
            'Cost Control Sheet',
        ]
        for index, title in enumerate(titles):
            merge = index == 3 and 9 or 8
            row_pos = self._report_title(
                ws, _p, row_pos, _xs, title, index, merge=merge)

        ws.set_horz_split_pos(row_pos)

        project_info = [
            'BU No. ' + project_id.operating_unit_id.name,
            'Job: ' + project_id.code + ' ' + project_id.name,
            'Event Date: ' +
            ('/'.join(project_id.date_start.split('-')) or '') + ' - ' +
            ('/'.join(project_id.date.split('-')) or ''),
            'Place: ' + (project_id.project_place or ''),
            'Export Time: ' + datetime.now(timezone('Asia/Bangkok'))
            .strftime('%d/%m/%Y %H:%M'),
            'Export By: ' +
            self.pool['res.users'].browse(cr, self.uid, self.uid)
            .display_name,
        ]
        for info in project_info:
            row_pos = self._report_header(ws, _p, row_pos, _xs, info, merge=9)

        row_pos = self._report_column_header(ws, _p, row_pos, _xs)

        quote_ids = project_id.quote_related_ids
        entries = []
        for quote_id in quote_ids:
            # No need quotation as state is cancel for no po
            if quote_id.state2 == 'cancel' and \
               not quote_id.project_related_id.purchase_related_ids.filtered(
                    lambda l: l.order_ref == quote_id and
                    l.state in ('approved', 'done')):
                continue
            # --
            line_and_parent = self._ordering_order_line(
                ws, _p, row_pos, quote_id)
            entries += line_and_parent

        total_price, total_estimate, total_po_price = [], [], []
        quote_price, quote_estimate, quote_po_price = [], [], []
        quote_price_2, quote_estimate_2, quote_po_price_2 = [], [], []
        custom_group_price, custom_group_estimate, custom_group_po_price = \
            [], [], []
        for entry in entries:
            data_obj = entry[1]
            if entry[0] == 'quote':
                quote_description = 'Quotation %s' % (data_obj.name)
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'quote'),
                    wl_ccs) + self._get_purchase_specs()
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.av_cell_style_decimal)
                quote_price = []
                quote_estimate = []
                quote_po_price = []
                quote_price_2 = []
                quote_estimate_2 = []
                quote_po_price_2 = []
            elif entry[0] == 'custom_group':
                custom_group_name = data_obj
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'custom_group'),
                    wl_ccs) + self._get_purchase_specs()
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.rt_cell_style_decimal)
                custom_group_price = []
                custom_group_estimate = []
                custom_group_po_price = []
            elif entry[0] == 'section':
                section_name = data_obj.name
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'section'),
                    wl_ccs) + self._get_purchase_specs()
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.rt_cell_style_decimal)
                section_pos = row_pos
            elif entry[0] == 'line':
                order_line_description = data_obj.name
                price_in_contract = 0
                estimate_cost = 0
                percent_margin = 0
                if data_obj.order_id.state2 != 'cancel':
                    price_in_contract = data_obj.price_unit * \
                        data_obj.product_uom_qty
                    estimate_cost = data_obj.purchase_price * \
                        data_obj.product_uom_qty
                    percent_margin = data_obj.sale_order_line_margin
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'order_line'),
                    wl_ccs)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.an_cell_style)
                line_row_pos = row_pos

                # purchase
                purchase_order_line_ids = purchase_order_line_obj.search(
                    cr, uid,
                    [('sale_order_line_ref_id', '=', data_obj.id),
                     ('order_id.state', 'in', ('approved', 'done'))])
                sale_layout_cat_id = self.pool.get('ir.model.data') \
                    .get_object_reference(
                        cr, uid, 'base', 'sale_layout_category_other')[1]
                if not data_obj.active and \
                   data_obj.sale_layout_cat_id.id == sale_layout_cat_id:
                    purchase_order_line_ids += purchase_order_line_obj.search(
                        cr, uid,
                        [('order_id.order_ref', '=', data_obj.order_id.id),
                         ('sale_order_line_ref_id', '=', False),
                         ('order_id.state', 'in', ('approved', 'done'))])
                purchase_order_line = purchase_order_line_obj.browse(
                    cr, uid, purchase_order_line_ids).mapped(
                    lambda l: (l.order_id, l.price_subtotal))
                res = [(k,
                        sum([y for (x, y) in purchase_order_line if x == k]))
                       for k in dict(purchase_order_line).keys()]
                i = 0
                for purchase_order, price_subtotal in dict(res).iteritems():
                    if i:
                        row_pos += 1
                    amount_margin = 'B%s - F%s' % \
                        (str(line_row_pos), str(row_pos))
                    gross_margin = '((B%s - F%s) / B%s) * 100' % \
                        (str(line_row_pos), str(row_pos),
                         str(line_row_pos))
                    ws.write(
                        row_pos - 1, 4, purchase_order.name,
                        style=self.an_cell_style)
                    ws.write(
                        row_pos - 1, 5, price_subtotal,
                        style=self.an_cell_style_decimal)
                    ws.write(
                        row_pos - 1, 6, purchase_order.partner_id.name,
                        style=self.an_cell_style)
                    ws.write(
                        row_pos - 1, 7, xlwt.Formula(amount_margin),
                        style=self.an_cell_style_decimal)
                    ws.write(row_pos - 1, 8,
                             xlwt.Formula('IF(ISERROR(%s), 0, %s)' %
                                          (gross_margin, gross_margin)),
                             style=self.an_cell_style_decimal)
                    i += 1

                if not i:
                    amount_margin = 'B%s - F%s' % \
                        (str(row_pos), str(row_pos))
                    gross_margin = '((B%s - F%s) / B%s) * 100' % \
                        (str(row_pos), str(row_pos), str(row_pos))
                    ws.write(row_pos - 1, 7, xlwt.Formula(amount_margin),
                             style=self.an_cell_style_decimal)
                    ws.write(row_pos - 1, 8,
                             xlwt.Formula('IF(ISERROR(%s), 0, %s)' %
                                          (gross_margin, gross_margin)),
                             style=self.an_cell_style_decimal)
            elif entry[0] == 'discount':
                c_specs = [
                    ('name', 1, 0, 'text', 'Discount Rate')
                ]
                c_specs += [('space_%s' % (i + 1), 1, 0, 'text', None)
                            for i in range(8)]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.rt_cell_style_decimal)
                c_specs = [
                    ('name', 1, 0, 'text', 'Discount'),
                    ('price_in_contract', 1, 0, 'number', data_obj, None,
                     self.an_cell_style_decimal),
                    ('estimate_cost', 1, 0, 'number', None, None,
                     self.an_cell_style_decimal),
                    ('percent_margin', 1, 0, 'number', None, None,
                     self.an_cell_style_decimal),
                ]
                c_specs += [('space_%s' % (i + 1), 1, 0, 'text', None)
                            for i in range(5)]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.an_cell_style)
                c_specs = [
                    ('name', 1, 0, 'text', 'Total Discount Rate'),
                    ('price_in_contract', 1, 0, 'number', None,
                     'B%s' % (str(row_pos))),
                    ('estimate_cost', 1, 0, 'number', None,
                     'C%s' % (str(row_pos))),
                    ('percent_margin', 1, 0, 'number', None,
                     'D%s' % (str(row_pos))),
                ]
                c_specs += [('space_%s' % (i + 1), 1, 0, 'text', None)
                            for i in range(5)]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.rt_cell_style_decimal)
            elif entry[0] == 'subtotal_section':
                sum_section_price = 'SUM(B%s:B%s)' % \
                    (str(section_pos + 1), row_pos)
                sum_section_estimate = 'SUM(C%s:C%s)' % \
                    (str(section_pos + 1), row_pos)
                sum_section_margin = 'B%s - C%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                sum_section_po_price = 'SUM(F%s:F%s)' % \
                    (str(section_pos + 1), row_pos)
                sum_section_amount_margin = 'B%s - F%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                sum_section_gross_margin = '((B%s - F%s) / B%s) * 100' % \
                    (str(row_pos + 1), str(row_pos + 1), str(row_pos + 1))
                c_specs = [
                    ('name', 1, 0, 'text', data_obj.get('name')),
                    ('price_in_contract', 1, 0, 'number', None,
                     sum_section_price),
                    ('estimate_cost', 1, 0, 'number', None,
                     sum_section_estimate),
                    ('percent_margin', 1, 0, 'number', None,
                     sum_section_margin),
                    ('purchase_number', 1, 0, 'text', None),
                    ('purchase_price', 1, 0, 'number', None,
                     sum_section_po_price),
                    ('purchase_note', 1, 0, 'text', None),
                    ('amount_margin', 1, 0, 'number', None,
                     sum_section_amount_margin),
                    ('gross_margin', 1, 0, 'number', None,
                     'IF(ISERROR(%s), 0, %s)' %
                     (sum_section_gross_margin, sum_section_gross_margin)),
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.rt_cell_style_decimal)
                custom_group_price.append('B%s' % (str(row_pos)))
                custom_group_estimate.append('C%s' % (str(row_pos)))
                custom_group_po_price.append('F%s' % (str(row_pos)))
                quote_price_2.append('B%s' % (str(row_pos)))
                quote_estimate_2.append('C%s' % (str(row_pos)))
                quote_po_price_2.append('F%s' % (str(row_pos)))
            elif entry[0] == 'subtotal_custom_group':
                sum_custom_group_price = \
                    custom_group_price and '+'.join(custom_group_price) or None
                sum_custom_group_estimate = \
                    custom_group_estimate and '+'.join(custom_group_estimate) \
                    or None
                sum_custom_group_margin = 'B%s - C%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                sum_custom_group_po_price = \
                    custom_group_po_price and '+'.join(custom_group_po_price) \
                    or None
                sum_custom_group_amount_margin = 'B%s - F%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                sum_custom_group_gross_margin = '((B%s - F%s) / B%s) * 100' % \
                    (str(row_pos + 1), str(row_pos + 1), str(row_pos + 1))
                c_specs = [
                    ('name', 1, 0, 'text', data_obj.get('name')),
                    ('price_in_contract', 1, 0, 'number', None,
                     sum_custom_group_price),
                    ('estimate_cost', 1, 0, 'number', None,
                     sum_custom_group_estimate),
                    ('percent_margin', 1, 0, 'number', None,
                     sum_custom_group_margin),
                    ('purchase_number', 1, 0, 'text', None),
                    ('purchase_price', 1, 0, 'number', None,
                     sum_custom_group_po_price),
                    ('purchase_note', 1, 0, 'text', None),
                    ('amount_margin', 1, 0, 'number', None,
                     sum_custom_group_amount_margin),
                    ('gross_margin', 1, 0, 'number', None,
                     'IF(ISERROR(%s), 0, %s)' %
                     (sum_custom_group_gross_margin,
                      sum_custom_group_gross_margin)),
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.rt_cell_style_decimal)
                quote_price.append('B%s' % (str(row_pos)))
                quote_estimate.append('C%s' % (str(row_pos)))
                quote_po_price.append('F%s' % (str(row_pos)))
            elif entry[0] == 'subtotal_quote':
                sum_quote_price = \
                    (quote_price and '+'.join(quote_price) or
                     '+'.join(quote_price_2) or '') + \
                    '-' + 'B%s' % (str(row_pos))
                sum_quote_estimate = \
                    quote_estimate and '+'.join(quote_estimate) or \
                    '+'.join(quote_estimate_2) or None
                sum_quote_margin = 'B%s - C%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                sum_quote_po_price = \
                    quote_po_price and '+'.join(quote_po_price) or \
                    '+'.join(quote_po_price_2) or None
                sum_quote_amount_margin = 'B%s - F%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                sum_quote_gross_margin = '((B%s - F%s) / B%s) * 100' % \
                    (str(row_pos + 1), str(row_pos + 1), str(row_pos + 1))
                c_specs = [
                    ('name', 1, 0, 'text', data_obj.get('name')),
                    ('price_in_contract', 1, 0, 'number', None,
                     sum_quote_price),
                    ('estimate_cost', 1, 0, 'number', None,
                     sum_quote_estimate),
                    ('percent_margin', 1, 0, 'number', None, sum_quote_margin),
                    ('purchase_number', 1, 0, 'text', None),
                    ('purchase_price', 1, 0, 'number', None,
                     sum_quote_po_price),
                    ('purchase_note', 1, 0, 'text', None),
                    ('amount_margin', 1, 0, 'number', None,
                     sum_quote_amount_margin),
                    ('gross_margin', 1, 0, 'number', None,
                     'IF(ISERROR(%s), 0, %s)' %
                     (sum_quote_gross_margin, sum_quote_gross_margin)),
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data,
                    row_style=self.av_cell_style_decimal)
                total_price.append('B%s' % (str(row_pos)))
                total_estimate.append('C%s' % (str(row_pos)))
                total_po_price.append('F%s' % (str(row_pos)))

        # Write PO Number as Quotation Number is False
        purchase_order_line_ids = purchase_order_line_obj.search(
            cr, uid,
            [('order_id.order_ref', '=', False),
             ('order_id.project_id', '=', project_id.id),
             ('order_id.state', 'in', ('approved', 'done'))])
        if len(purchase_order_line_ids):
            purchase_order_line = purchase_order_line_obj.browse(
                cr, uid, purchase_order_line_ids).mapped(
                lambda l: (l.order_id, l.price_subtotal))
            res = [(k,
                    sum([y for (x, y) in purchase_order_line if x == k]))
                   for k in dict(purchase_order_line).keys()]
            for purchase_order, price_subtotal in dict(res).iteritems():
                amount_margin = 'B%s - F%s' % \
                    (str(row_pos + 1), str(row_pos + 1))
                gross_margin = '((B%s - F%s) / B%s) * 100' % \
                    (str(row_pos + 1), str(row_pos + 1),
                     str(row_pos + 1))
                ws.write(row_pos, 0, '', style=self.an_cell_style)
                ws.write(row_pos, 1, '', style=self.an_cell_style)
                ws.write(row_pos, 2, '', style=self.an_cell_style)
                ws.write(row_pos, 3, '', style=self.an_cell_style)
                ws.write(
                    row_pos, 4, purchase_order.name,
                    style=self.an_cell_style)
                ws.write(
                    row_pos, 5, price_subtotal,
                    style=self.an_cell_style_decimal)
                ws.write(
                    row_pos, 6, purchase_order.partner_id.name,
                    style=self.an_cell_style)
                ws.write(
                    row_pos, 7, xlwt.Formula(amount_margin),
                    style=self.an_cell_style_decimal)
                ws.write(
                    row_pos, 8,
                    xlwt.Formula('IF(ISERROR(%s), 0, %s)' %
                                 (gross_margin, gross_margin)),
                    style=self.an_cell_style_decimal)
                row_pos += 1
                total_po_price.append('F%s' % (str(row_pos)))

        # totals
        sum_price = total_price and '+'.join(total_price) or '0'
        sum_estimate = total_estimate and '+'.join(total_estimate) or '0'
        sum_margin = 'B%s - C%s' % (str(row_pos + 1), str(row_pos + 1))
        sum_po_price = total_po_price and '+'.join(total_po_price) or '0'
        sum_amount_margin = 'B%s - F%s' % (str(row_pos + 1), str(row_pos + 1))
        sum_gross_margin = '((B%s - F%s) / B%s) * 100' % \
            (str(row_pos + 1), str(row_pos + 1), str(row_pos + 1))
        grand_total_price = 'B%s' % (str(row_pos + 1))
        grand_total_estimate = 'C%s' % (str(row_pos + 1))
        grand_total_po_price = 'F%s' % (str(row_pos + 1))

        ws.write(row_pos, 0, 'Total All Quotation and Total All P/O',
                 style=self.av_cell_style_decimal)
        ws.write(row_pos, 1, xlwt.Formula(sum_price),
                 style=self.av_cell_style_decimal)
        ws.write(row_pos, 2, xlwt.Formula(sum_estimate),
                 style=self.av_cell_style_decimal)
        ws.write(row_pos, 3, xlwt.Formula(sum_margin),
                 style=self.av_cell_style_decimal)
        ws.write(row_pos, 4, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 5, xlwt.Formula(sum_po_price),
                 style=self.av_cell_style_decimal)
        ws.write(row_pos, 6, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 7, xlwt.Formula(sum_amount_margin),
                 style=self.av_cell_style_decimal)
        ws.write(row_pos, 8,
                 xlwt.Formula('IF(ISERROR(%s), 0, %s)' %
                              (sum_gross_margin, sum_gross_margin)),
                 style=self.av_cell_style_decimal)
        row_pos += 1

        # Space before expense section
        c_specs = [
            ('space', 9, 0, 'text', ''),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.an_cell_style)

        # Expense
        expense_line_ids = expense_line_obj.search(
            cr, uid,
            [('analytic_account', '=', project_id.analytic_account_id.id)])
        expense_line = expense_line_obj.browse(cr, uid, expense_line_ids) \
            .filtered(lambda l:
                      (l.expense_id.is_employee_advance is False or
                       l.expense_id.is_advance_clearing is True) and
                      l.expense_id.state in ('validate', 'done', 'paid'))
        cell_style = xlwt.easyxf(
            'pattern: pattern solid, fore_color gray25;' + _xs['bold'] +
            _xs['borders_all'] + _xs['right'],
            num_format_str=report_xls.decimal_format)
        total_price = []
        # Header
        c_specs = self._get_expense_specs(
            name='Expense and Advance Cost', number='Expense No.',
            price=['text', 'Price', None], employee='Employee')
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        # Traveling expense
        c_specs = self._get_expense_specs(
            name='Traveling Expenses', price=['text', None, None])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.rt_cell_style_decimal)
        traveling_expense_pos = row_pos
        traveling_expense_categ_id = \
            self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'base', 'product_category_3')[1]
        lines = expense_line.filtered(
            lambda l: l.product_id.categ_id.id == traveling_expense_categ_id) \
            .sorted(lambda k: k.expense_id.number)
        for line in lines:
            c_specs = self._get_expense_specs(
                name=line.ref, number=line.expense_id.number,
                employee=line.expense_id.employee_request_id.name,
                price=['number', line.amount_line_untaxed, None])
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data,
                row_style=self.an_cell_style_decimal)
        sum_traveling_expense_price = None
        if lines:
            sum_traveling_expense_price = 'SUM(F%s:F%s)' % \
                (str(traveling_expense_pos + 1), str(row_pos))
        c_specs = self._get_expense_specs(
            name='Total Traveling Expenses',
            price=['number', None, sum_traveling_expense_price])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.rt_cell_style_decimal)
        total_price.append('F%s' % (str(row_pos)))
        # petty cash
        c_specs = self._get_expense_specs(
            name='Petty Cash', price=['text', None, None])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.rt_cell_style_decimal)
        petty_cash_pos = row_pos
        lines = expense_line.filtered(
            lambda l: l.expense_id.pay_to == 'pettycash') \
            .sorted(lambda k: k.expense_id.number)
        for line in lines:
            c_specs = self._get_expense_specs(
                name=line.ref, number=line.expense_id.number,
                employee=line.expense_id.employee_request_id.name,
                price=['number', line.amount_line_untaxed, None])
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data,
                row_style=self.an_cell_style_decimal)
        sum_petty_cash_price = None
        if lines:
            sum_petty_cash_price = 'SUM(F%s:F%s)' % \
                (str(petty_cash_pos + 1), str(row_pos))
        c_specs = self._get_expense_specs(
            name='Total Petty Cash',
            price=['number', None, sum_petty_cash_price])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.rt_cell_style_decimal)
        total_price.append('F%s' % (str(row_pos)))
        # Other expense
        c_specs = self._get_expense_specs(
            name='Other Expense', price=['text', None, None])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.rt_cell_style_decimal)
        other_expense_pos = row_pos
        lines = expense_line.filtered(
            lambda l: l.product_id.categ_id.id != traveling_expense_categ_id
            and l.expense_id.pay_to != 'pettycash') \
            .sorted(lambda k: k.expense_id.number)
        for line in lines:
            c_specs = self._get_expense_specs(
                name=line.ref, number=line.expense_id.number,
                employee=line.expense_id.employee_request_id.name,
                price=['number', line.amount_line_untaxed, None])
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data,
                row_style=self.an_cell_style_decimal)
        sum_other_expense_price = None
        if lines:
            sum_other_expense_price = 'SUM(F%s:F%s)' % \
                (str(other_expense_pos + 1), str(row_pos))
        c_specs = self._get_expense_specs(
            name='Total Other Expense',
            price=['number', None, sum_other_expense_price])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.rt_cell_style_decimal)
        total_price.append('F%s' % (str(row_pos)))
        # Total
        sum_expense_price = '+'.join(total_price)
        c_specs = self._get_expense_specs(
            name='Total Expense and Advance Cost',
            price=['number', None, sum_expense_price])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=cell_style)
        grand_total_po_price += ' + F%s' % (str(row_pos))

        # Space before direct invoice section
        c_specs = [
            ('space', 9, 0, 'text', ''),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.an_cell_style)

        # Direct invoice
        invoice_line_ids = invoice_line_obj.search(
            cr, uid,
            [('account_analytic_id', '=', project_id.analytic_account_id.id),
             ('invoice_id.type', 'in', ('out_invoice', 'out_refund')),
             ('invoice_id.state', 'in', ('open', 'paid')),
             ('invoice_id.quote_ref_id', '=', False)])
        invoice_lines = invoice_line_obj.browse(cr, uid, invoice_line_ids)
        cell_style = xlwt.easyxf(
            'pattern: pattern solid, fore_color gray25;' + _xs['bold'] +
            _xs['borders_all'] + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # Header
        c_specs = self._get_invoice_specs(
            name='Other Income / Revenue', number='Invoice No.',
            price=['text', 'Price', None], customer='Customer')
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        invoice_pos = row_pos
        # Detail
        for line in invoice_lines:
            c_specs = self._get_invoice_specs(
                name=line.name, number=line.invoice_id.number,
                price=['number', line.quantity * line.price_unit, None],
                customer=line.invoice_id.partner_id.display_name)
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data,
                row_style=self.an_cell_style_decimal)
        # Total
        sum_invoice_price = None
        if invoice_lines:
            sum_invoice_price = 'SUM(B%s: B%s)' % \
                (str(invoice_pos + 1), str(row_pos))
        c_specs = self._get_invoice_specs(
            name='Total Other Income / Revenue',
            price=['number', None, sum_invoice_price])
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        grand_total_price += ' + B%s' % (str(row_pos))

        # Space before grand total section
        c_specs = [
            ('space', 9, 0, 'text', ''),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.an_cell_style)

        # Grand total
        grand_total_percent_margin = 'B%s - C%s' % \
            (str(row_pos + 1), str(row_pos + 1))
        grand_total_amount_margin = 'B%s - F%s' % \
            (str(row_pos + 1), str(row_pos + 1))
        grand_total_gross_margin = '((B%s - F%s) / B%s) * 100' % \
            (str(row_pos + 1), str(row_pos + 1), str(row_pos + 1))
        c_specs = [
            ('name', 1, 0, 'text',
             'Grand Total (Quotation, Direct Invoice, PO and Expenses)'),
            ('price_in_contract', 1, 0, 'number', None, grand_total_price),
            ('estimate_cost', 1, 0, 'number', None, grand_total_estimate),
            ('percent_margin', 1, 0, 'number', None,
             grand_total_percent_margin),
            ('purchase_number', 1, 0, 'text', None),
            ('purchase_price', 1, 0, 'number', None, grand_total_po_price),
            ('purchase_note', 1, 0, 'text', None),
            ('amount_margin', 1, 0, 'number', None, grand_total_amount_margin),
            ('gross_margin', 1, 0, 'number', None,
             'IF(ISERROR(%s), 0, %s)' %
             (grand_total_gross_margin, grand_total_gross_margin)),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.av_cell_style_decimal)

        # --
        if project_id.adjustment_ids:
            # Space before adjustment section
            c_specs = [
                ('space', 9, 0, 'text', ''),
            ]
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.an_cell_style)
            adjustment_obj = self.pool.get('project.adjustment')
            ws.write(
                row_pos, 0, 'Adjustment', style=self.av_cell_style_decimal)
            ws.write(row_pos, 1, 'Amount', style=self.av_cell_style_decimal)
            for i in range(2, 9):
                ws.write(row_pos, i, '', style=self.av_cell_style_decimal)
            row_pos += 1
            for adjustment_id in project_id.adjustment_ids.ids:
                adjustment_line = adjustment_obj.browse(
                    self.cr, self.uid,
                    adjustment_id, context=self.context)
                ws.write(
                    row_pos, 0,
                    adjustment_line.name,
                    style=self.an_cell_style)
                ws.write(
                    row_pos, 1,
                    adjustment_line.amount,
                    style=self.an_cell_style_decimal)
                for i in range(2, 9):
                    ws.write(row_pos, i, '', style=self.an_cell_style)
                row_pos += 1
            ws.write(
                row_pos, 0, 'Total Adjustment',
                style=self.av_cell_style_decimal)
            ws.write(row_pos, 1, project_id.adjustment_amount,
                     style=self.av_cell_style_decimal)
            for i in range(2, 9):
                ws.write(row_pos, i, '', style=self.av_cell_style_decimal)
            row_pos += 1

        # Write Footer
        row_pos += 4
        department_obj = self.pool.get('hr.department')
        department_ids = department_obj.search(
            self.cr, self.uid, [('name', '=',
                                 project_id.operating_unit_id.name)],
            context=self.context)
        if len(department_ids) > 1:
            department_ids = [department_ids[0]]
        department = department_obj.browse(
            self.cr, self.uid, department_ids, context=context)
        cell_text_style = xlwt.easyxf(_xs['right'])
        cell_value_style = xlwt.easyxf('borders: bottom thin;')
        cell_center_style = xlwt.easyxf(_xs['center'])
        c_specs = [
            ('client_text', 1, 0, 'text', 'Client', None, cell_text_style),
            ('client_value', 4, 0, 'text', project_id.partner_id.display_name,
             None, cell_value_style),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('address_text', 1, 0, 'text', 'Address', None, cell_text_style),
            ('address_value', 4, 0, 'text',
             ' '.join(list(filter(lambda l: l is not False,
                                  [project_id.partner_id.street,
                                   project_id.partner_id.street2]))),
             None, cell_value_style),
            ('tel_text', 1, 0, 'text', 'Tel.', None, cell_text_style),
            ('tel_value', 1, 0, 'text', project_id.partner_id.phone, None,
             cell_value_style),
            ('fax_text', 1, 0, 'text', 'Fax', None, cell_text_style),
            ('fax_value', 1, 0, 'text', project_id.partner_id.fax, None,
             cell_value_style),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        c_specs = [
            ('contract_person_text', 1, 0, 'text', 'Contact Person', None,
             cell_text_style),
            ('contract_person_value', 4, 0, 'text',
             ', '.join([l.display_name
                        for l in project_id.partner_id.child_ids]), None,
             cell_value_style),
            ('mobile_text', 1, 0, 'text', 'Mobile.', None, cell_text_style),
            ('mobile_value', 1, 0, 'text', project_id.partner_id.mobile, None,
             cell_value_style),
            ('email_text', 1, 0, 'text', 'E-Mail', None, cell_text_style),
            ('email_value', 1, 0, 'text', project_id.partner_id.email, None,
             cell_value_style),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        # Insert checkbox
        ws.insert_bitmap(
            '%s/static/description/checkbox.bmp' % report_dir, row_pos + 1, 0,
            x=400, y=1, scale_x=0.5, scale_y=0.5
        )
        ws.insert_bitmap(
            '%s/static/description/checkbox.bmp' % report_dir, row_pos + 1, 5,
            x=120, y=1, scale_x=0.5, scale_y=0.5
        )
        c_specs = [
            ('approved_value', 1, 0, 'text', None),
            ('approved_text', 4, 0, 'text', 'Approved'),
            ('below_standard_value', 1, 0, 'text', None),
            ('below_standard_text', 1, 0, 'text', 'Below Standard'),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos + 1, row_data)
        c_specs = [
            ('space_1', 1, 0, 'text', None),
            ('signature_value_1', 4, 0, 'text', None, None, cell_value_style),
            ('space_2', 1, 0, 'text', None),
            ('signature_value_2', 2, 0, 'text', None, None, cell_value_style),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos + 1, row_data)
        c_specs = [
            ('space_1', 1, 0, 'text', None),
            ('signature_text_1', 4, 0, 'text',
             '(%s)' % department.manager_id.display_name, None,
             cell_center_style),
            ('space_2', 1, 0, 'text', None),
            ('signature_text_2', 2, 0, 'text', '(Sermkhun Kunawong)', None,
             cell_center_style),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # wl_ccs = _p.wanted_list_cost_control_sheet
        self.cost_control_sheet_template.update(
            _p.template_update_cost_control_sheet)
        self.projects = self.pool.get('project.project')
        self._cost_control_sheet_report(_p, _xs, data, objects, wb)


CostControlSheetReportXls(
    'report.cost.control.sheet.xls',
    'project.project',
    parser=CostControlSheetReportXlsParser)
