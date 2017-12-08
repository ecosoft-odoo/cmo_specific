# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import xlwt
from xlwt.Style import default_style
from datetime import datetime

from openerp.exceptions import Warning as UserError
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _

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
                'order_line': [1, 0, 'number', _render("price_in_contract")],
                },
            'estimate_cost': {
                'quote': [1, 0, 'text', None],
                'custom_group': [1, 0, 'text', None],
                'section': [1, 0, 'text', None],
                'order_line': [1, 0, 'number', _render("estimate_cost")],
                },
            'percent_margin': {
                'quote': [1, 0, 'text', None],
                'custom_group': [1, 0, 'text', None],
                'section': [1, 0, 'text', None],
                'order_line': [1, 0, 'number', _render("percent_margin")],
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

    def _report_title(self, ws, _p, row_pos, _xs, title, offset=0, merge=1):
        cell_style = xlwt.easyxf(
            _xs['center'] + 'font: color blue, bold false, height 220;')
        c_specs = [
            ('report_name', merge, 0, 'text', title),
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
            'align: vertical center, horizontal center;' + _xs['bold'])
        parent_titles = [
            {
                'text': 'Description',
                'size': 40,
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
                'text': '% Margin',
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
                'text': 'Expense+Advance',
                'size': 20,
                'col_span': 4,
                'row_span': 1,
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
            {
                'text': 'No.',
                'size': 20,
                'col_pos': 7,
            },
            {
                'text': 'Description',
                'size': 20,
                'col_pos': 8,
            },
            {
                'text': 'Employee',
                'size': 20,
                'col_pos': 9,
            },
            {
                'text': 'Price',
                'size': 20,
                'col_pos': 10,
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

    def _ordering_order_line(self, ws, _p, row_pos, quote_id):
        cr = self.cr
        uid = self.uid
        context = self.context
        section_obj = self.pool.get('sale_layout.category')
        order_line_obj = self.pool.get('sale.order.line')
        line_and_parent = []

        def _line_order_get(custom_groups=None):
            line_get = []
            if custom_groups:
                cr.execute(
                    "SELECT sale_layout_cat_id, COUNT(id) FROM sale_order_line "
                    "WHERE order_id = %s AND order_lines_group = 'before' "
                    "GROUP BY sale_layout_cat_id "
                    "ORDER BY sale_layout_cat_id ASC"
                    % (quote_id.id))
            else:
                cr.execute(
                    "SELECT sale_layout_cat_id, COUNT(id) FROM sale_order_line "
                    "WHERE order_id = %s GROUP BY sale_layout_cat_id "
                    "ORDER BY sale_layout_cat_id ASC"
                    % (quote_id.id))
            section_ids = [x[0] for x in cr.fetchall()]
            for section_id in section_ids:
                section_id = section_obj.browse(
                    cr, uid, section_id, context=context)
                order_line_ids = order_line_obj.search(cr, uid, [
                    ('sale_layout_cat_id', '=', section_id.id),
                    ('order_id', '=', quote_id.id),
                    ('sale_layout_custom_group', '=', custom_groups),
                ])
                if order_line_ids:
                    line_get.append(('section', section_id))
                line_list = [('line', order_line_obj.browse(
                    cr, uid, x, context=context)) for x in order_line_ids]
                line_get += line_list
            return line_get

        quote_data = ('quote', quote_id)
        line_and_parent.append(quote_data)
        cr.execute(
            "SELECT sale_layout_custom_group, COUNT(id)  FROM sale_order_line "
            "WHERE order_id = %s GROUP BY sale_layout_custom_group "
            "ORDER BY sale_layout_custom_group ASC"
            % (quote_id.id))
        custom_groups = [x[0] for x in cr.fetchall()]
        if len(custom_groups) > 1:
            for custom_group in custom_groups:
                line_and_parent.append(('custom_group', custom_group))
                line_and_parent += _line_order_get(custom_group)
        else:
            line_and_parent += _line_order_get()
        return line_and_parent

    def _cost_control_sheet_report(self, _p, _xs, data, objects, wb):
        cr = self.cr
        uid = self.uid
        context = self.context

        wl_ccs = _p.wanted_list_cost_control_sheet
        template = self.cost_control_sheet_template
        project_obj = self.pool['project.project']
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        expense_line_obj = self.pool.get('hr.expense.line')
        project_id = project_obj.browse(
            cr, uid, data['project_id'], context=context)

        sheet_name = "Cost Control Sheet"
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        company_id = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        titles = [
            company_id.name or '',
            company_id.street or '',
            'TEL. %s  FAX %s  WEB %s  E-mail %s ' % (
                company_id.phone or '-',
                company_id.fax or '-',
                company_id.website or '-',
                company_id.email or '-'
                ),
            'Cost Control Sheet',
        ]
        for title in titles:
            row_pos = self._report_title(ws, _p, row_pos, _xs, title, merge=11)

        project_info = [
            'BU No. ' + project_id.operating_unit_id.name,
            'Job: ' + project_id.project_number + ' ' + project_id.name,
            'Event Date: ' +
            ('/'.join(project_id.date_start.split('-')) or '') + ' - ' +
            ('/'.join(project_id.date.split('-')) or ''),
            'Place: ' + (project_id.project_place or ''),
        ]
        for info in project_info:
            row_pos = self._report_header(ws, _p, row_pos, _xs, info, merge=11)

        row_pos = self._report_column_header(ws, _p, row_pos, _xs)
        ws.set_horz_split_pos(row_pos)

        hr_row_pos = row_pos
        quote_ids = project_id.quote_related_ids
        entries = []
        for quote_id in quote_ids:
            line_and_parent = self._ordering_order_line(
                ws, _p, row_pos, quote_id)
            entries += line_and_parent

        for entry in entries:
            data_obj = entry[1]
            if entry[0] == 'quote':
                quote_description = 'Quotation %s' % (data_obj.name)
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'quote'),
                    wl_ccs)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.av_cell_style_decimal)
            elif entry[0] == 'custom_group':
                custom_group_name = data_obj
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'custom_group'),
                    wl_ccs)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.rt_cell_style_decimal)
            elif entry[0] == 'section':
                section_name = data_obj.name
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'section'),
                    wl_ccs)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.rt_cell_style_decimal)
            elif entry[0] == 'line':
                order_line_description = data_obj.name
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

                # purchase
                purchase_order_line_ids = purchase_order_line_obj.search(
                    cr, uid, [
                        ('sale_order_line_ref_id', '=', data_obj.id),
                        ('state', 'in', ('confirmed', 'approved', 'done')),
                    ])
                if purchase_order_line_ids:
                    purchase_row_pos = row_pos
                    for row_i, purchase_order_line_id in enumerate(
                            purchase_order_line_ids):
                        order_line_id = purchase_order_line_obj.browse(
                            self.cr, self.uid,
                            purchase_order_line_id, context=self.context)
                        ws.write(
                            purchase_row_pos + row_i - 1, 4,
                            order_line_id.order_id.name,
                            style=self.an_cell_style)
                        ws.write(
                            purchase_row_pos + row_i - 1, 5,
                            order_line_id.price_subtotal,
                            style=self.an_cell_style)
                        ws.write(
                            purchase_row_pos + row_i - 1, 6,
                            order_line_id.order_id.partner_id.name,
                            style=self.an_cell_style)
                        row_pos += row_i

        expense_line_ids = expense_line_obj.search(cr, uid, [
             ('analytic_account', '=', project_id.analytic_account_id.id),
        ])
        if expense_line_ids:
            for row_i, expense_line_id in enumerate(expense_line_ids):
                expense_line_id = expense_line_obj.browse(
                    self.cr, self.uid,
                    expense_line_id, context=self.context)
                ws.write(
                    hr_row_pos + row_i, 7,
                    expense_line_id.expense_id.number,
                    style=self.an_cell_style)
                ws.write(
                    hr_row_pos + row_i, 8,
                    expense_line_id.ref or '',
                    style=self.an_cell_style)
                ws.write(
                    hr_row_pos + row_i, 9,
                    expense_line_id.expense_id.employee_request_id.name or '',
                    style=self.an_cell_style)
                ws.write(
                    hr_row_pos + row_i, 10,
                    expense_line_id.amount_line_untaxed,
                    style=self.an_cell_style)

        # totals
        sum_price = 'SUM(B%s:B%s)' % (str(hr_row_pos+1), str(row_pos))
        sum_estimate = 'SUM(C%s:C%s)' % (str(hr_row_pos+1), str(row_pos))
        sum_margin = '(B%s - C%s) * 100.0 / B%s' % (
            str(row_pos+1), str(row_pos+1), str(row_pos+1))
        sum_po_price = 'SUM(F%s:F%s)' % (str(hr_row_pos+1), str(row_pos))
        sum_hr_price = 'SUM(K%s:K%s)' % (str(hr_row_pos+1), str(row_pos))

        ws.write(row_pos, 0, 'Totals', style=self.av_cell_style_decimal)
        ws.write(row_pos, 1, xlwt.Formula(sum_price), style=self.av_cell_style_decimal)
        ws.write(row_pos, 2, xlwt.Formula(sum_estimate), style=self.av_cell_style_decimal)
        ws.write(row_pos, 3, xlwt.Formula(sum_margin), style=self.av_cell_style_decimal)
        ws.write(row_pos, 4, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 5, xlwt.Formula(sum_po_price), style=self.av_cell_style_decimal)
        ws.write(row_pos, 6, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 7, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 8, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 9, '', style=self.av_cell_style_decimal)
        ws.write(row_pos, 10, xlwt.Formula(sum_hr_price), style=self.av_cell_style_decimal)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        wl_ccs = _p.wanted_list_cost_control_sheet
        self.cost_control_sheet_template.update(
            _p.template_update_cost_control_sheet)
        fy = self.pool.get('account.fiscalyear').browse(
            self.cr, self.uid, data['fiscalyear_id'], context=self.context)
        self.fiscalyear = fy
        self.projects = self.pool.get('project.project')
        self._cost_control_sheet_report(_p, _xs, data, objects, wb)

CostControlSheetReportXls(
    'report.cost.control.sheet.xls',
    'project.project',
    parser=CostControlSheetReportXlsParser)
