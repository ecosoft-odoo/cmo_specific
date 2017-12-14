# -*- coding: utf-8 -*-
import logging
import xlwt
from xlwt.Style import default_style
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import _render
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class PaymentReceiptIntransitReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PaymentReceiptIntransitReportXlsParser, self).__init__(
            cr, uid, name, context=context)
        move_line_obj = self.pool.get('account.move.line')
        self.context = context
        wl_pin = move_line_obj._xls_payment_receipt_intransit_fields(
            cr, uid, context)
        tmpl_pin_upd = move_line_obj._xls_payment_receipt_intransit_template(
            cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list_payment_receipt_intransit': wl_pin,
            'template_update_payment_receipt_intransit': tmpl_pin_upd,
            '_': _,
        })


class PaymentReceiptIntransitReportXls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(PaymentReceiptIntransitReportXls, self).__init__(
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
        self.payment_receipt_intransit_template = {
            'date': {
                'header': [
                    1, 20, 'text', _render("_('Date Posted')"),
                    None, self.rh_cell_style_center],
                'move_line': [1, 0, 'date', _render(
                    "datetime.strptime(move_line_date,'%Y-%m-%d') or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None],
            },
            'ref': {
                'header': [
                    1, 20, 'text', _render("_('Number')"),
                    None, self.rh_cell_style_center],
                'move_line': [1, 0, 'text', _render("move_line_ref")],
            },
            'name': {
                'header': [
                    1, 20, 'text', _render("_('Name')"),
                    None, self.rh_cell_style_center],
                'move_line': [1, 0, 'text', _render("move_line_name")],
            },
            'cheque_number': {
                'header': [
                    1, 20, 'text', _render("_('Cheque Number')"),
                    None, self.rh_cell_style_center],
                'move_line': [1, 0, 'text', _render("move_line_cheque or ''")],
            },
            'amount': {
                'header': [
                    1, 20, 'text', _render("_('amount')"),
                    None, self.rh_cell_style_center],
                'move_line': [1, 0, 'number', _render("move_line_amount")],
            },
        }

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

    def _payment_receipt_intransit_report(self, _p, _xs, data, objects, wb):
        cr = self.cr
        uid = self.uid
        context = self.context

        wl_pin = _p.wanted_list_payment_receipt_intransit
        template = self.payment_receipt_intransit_template

        sheet_name = "%s Intransit" % str(data['doc_type']).title()
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
            'Bank %s' % sheet_name,
        ]
        for title in titles:
            row_pos = self._report_title(ws, _p, row_pos, _xs, title, merge=5)

        c_specs = map(
            lambda x: self.render(
                x, template, 'header',
                render_space={'_': _p._}),
            wl_pin)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)

        cr.execute(
            "SELECT account_move_line.date, account_move_line.ref, "
            "account_move_line.name, account_voucher.number_cheque, "
            "account_move_line.debit, account_move_line.credit "
            "FROM account_move_line INNER JOIN account_voucher ON "
            "account_voucher.move_id = account_move_line.move_id "
            "WHERE account_move_line.reconcile_id IS NULL "
            "AND account_move_line.reconcile_ref IS NULL "
            "AND account_voucher.type = %s "
            "AND account_move_line.date <= %s "
            "AND account_voucher.state = 'posted' ",
            (data['doc_type'], data['posted_date'])
        )
        entries = cr.fetchall()
        move_row_pos = row_pos + 1

        for entry in entries:
            move_line_date = entry[0]
            move_line_ref = entry[1]
            move_line_name = entry[2]
            move_line_cheque = entry[3]
            if data['doc_type'] == 'payment':
                move_line_amount = entry[5] - entry[4]
            else:  # type = 'receipt'
                move_line_amount = entry[4] - entry[5]

            c_specs = map(
                lambda x: self.render(
                    x, template, 'move_line'),
                wl_pin)
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.an_cell_style)

        sum_amount = 'SUM(E%s:E%s)' % (str(move_row_pos), str(row_pos))
        ws.write(row_pos, 3, 'Totals', style=self.av_cell_style_decimal)
        ws.write(row_pos, 4, xlwt.Formula(sum_amount),
                 style=self.av_cell_style_decimal)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # wl_pin = _p.wanted_list_payment_receipt_intransit
        self.payment_receipt_intransit_template.update(
            _p.template_update_payment_receipt_intransit)
        self._payment_receipt_intransit_report(_p, _xs, data, objects, wb)


PaymentReceiptIntransitReportXls(
    'report.payment.intransit',
    'account.move.line',
    parser=PaymentReceiptIntransitReportXlsParser)

PaymentReceiptIntransitReportXls(
    'report.receipt.intransit',
    'account.move.line',
    parser=PaymentReceiptIntransitReportXlsParser)
