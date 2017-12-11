# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import xlwt
from datetime import datetime

from openerp.exceptions import Warning as UserError
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _

_logger = logging.getLogger(__name__)


_ir_translation_name = 'account.asset.report'


class AssetReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AssetReportXlsParser, self).__init__(
            cr, uid, name, context=context)
        asset_obj = self.pool.get('account.asset')
        self.context = context
        wl_acq = asset_obj._xls_acquisition_fields(cr, uid, context)
        wl_act = asset_obj._xls_active_fields(cr, uid, context)
        wl_rem = asset_obj._xls_removal_fields(cr, uid, context)
        tmpl_acq_upd = asset_obj._xls_acquisition_template(cr, uid, context)
        tmpl_act_upd = asset_obj._xls_active_template(cr, uid, context)
        tmpl_rem_upd = asset_obj._xls_removal_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list_acquisition': wl_acq,
            'wanted_list_active': wl_act,
            'wanted_list_removal': wl_rem,
            'template_update_acquisition': tmpl_acq_upd,
            'template_update_active': tmpl_act_upd,
            'template_update_removal': tmpl_rem_upd,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        res = translate(self.cr, _ir_translation_name, 'report', lang, src)
        return res or src


class AssetReportXls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(AssetReportXls, self).__init__(
            name, table, rml, parser, header, store)

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
        self.acquisition_template = {
            'account': {
                'header': [1, 20, 'text', _render("_('รหัส')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'text',
                    _render("asset.number")],
                'totals': [
                    1, 0, 'text', _render("_('รวม')"),
                    None, self.rt_cell_style]},
            'name': {
                'header': [1, 40, 'text', _render("_('ชื่อสินทรัพย์')")],
                'asset_view': [1, 0, 'text', _render("asset.profile_id.name")],
                'asset': [1, 0, 'text', _render("asset.name or ''")],
                'totals': [1, 0, 'text', None]},
            'operating_unit_id': {
                'header': [1, 20, 'text', _render("_('แผนก')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render(
                    "asset.operating_unit_id.code or '-'")],
                'totals': [1, 0, 'text', None]},
            'code': {
                'header': [1, 20, 'text', _render("_('เอกสารอ้างอิง')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render("asset.code or ''")],
                'totals': [1, 0, 'text', None]},
            'date_start': {
                'header': [1, 20, 'text', _render("_('วันที่ซื้อหรือได้มา')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'date',
                    _render("asset.date_start and "
                            "datetime.strptime(asset.purchase_date,'%Y-%m-%d') "
                            "or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'depreciation_base': {
                'header': [
                    1, 18, 'text', _render("_('ราคาทรัพย์สินที่ซื้อหรือได้มา')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None,
                    _render("asset_formula"), self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.purchase_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("asset_total_formula"),
                    self.rt_cell_style_decimal]},
            'salvage_value': {
                'header': [
                    1, 18, 'text', _render("_('ราคาซาก')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("salvage_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.salvage_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("salvage_total_formula"),
                    self.rt_cell_style_decimal]},
        }

        self.active_template = {
            'account': {
                'header': [1, 20, 'text', _render("_('รหัส')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'text',
                    _render("asset.number")],
                'totals': [
                    1, 0, 'text', _render("_('รวม')"),
                    None, self.rt_cell_style]},
            'name': {
                'header': [1, 40, 'text', _render("_('ชื่อสินทรัพย์')")],
                'asset_view': [1, 0, 'text', _render("asset.profile_id.name")],
                'asset': [1, 0, 'text', _render("asset.name or ''")],
                'totals': [1, 0, 'text', None]},
            'date_purchase': {
                'header': [1, 20, 'text', _render("_('วันที่ซื้อหรือได้มา')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'date',
                    _render("asset.date_start and "
                            "datetime.strptime(asset.purchase_date,'%Y-%m-%d') "
                            "or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'date_start': {
                'header': [1, 20, 'text', _render("_('วันที่เริ่มคำนวณค่าเสื่อม')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'date',
                    _render("asset.date_start and "
                            "datetime.strptime(asset.date_start,'%Y-%m-%d') "
                            "or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'purchase_value': {
                'header': [
                    1, 18, 'text', _render("_('ราคาทรัพย์สินที่ซื้อหรือได้มา')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("purchase_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.purchase_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("purchase_total_formula"),
                    self.rt_cell_style_decimal]},
            'asset_value_previous': {
                'header': [
                    1, 22, 'text', _render("_('มูลค่าต้นทุนในวันสุดท้ายของรอบระยะบัญชีก่อน')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("asset_value_previous_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.asset_value_previous"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("asset_value_previous_total_formula"),
                    self.rt_cell_style_decimal]},
            'remaining_value': {
                'header': [
                    1, 18, 'text', _render("_('มูลค่าต้นทุนหลังจากค่าเสื่อมราคาแล้วจนถึงปัจจุบัน')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("remaining_value_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.remaining_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("remaining_value_total_formula"),
                    self.rt_cell_style_decimal]},
            'percent': {
                'header': [
                    1, 18, 'text', _render("_('อัตราร้อยละ')"),
                    None, self.rh_cell_style_right],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'number', _render("100.0 / asset.method_number"),
                    None, self.an_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'operating_unit_id': {
                'header': [1, 20, 'text', _render("_('แผนก')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render(
                    "asset.operating_unit_id.code or '-'")],
                'totals': [1, 0, 'text', None]},
            'code': {
                'header': [1, 20, 'text', _render("_('เอกสารอ้างอิง')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render("asset.code or ''")],
                'totals': [1, 0, 'text', None]},
            'salvage_value': {
                'header': [
                    1, 18, 'text', _render("_('ราคาซาก')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("salvage_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.salvage_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("salvage_total_formula"),
                    self.rt_cell_style_decimal]},
            'asset_line_amount': {
                'header': [
                    1, 22, 'text', _render("_('ค่าเสื่อมราคาที่หักในรอบระยะเวลาบัญชีนี้')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("asset_line_amount_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.asset_line_amount"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("asset_line_amount_total_formula"),
                    self.rt_cell_style_decimal]},
            'depreciated_value': {
                'header': [
                    1, 18, 'text', _render("_('ค่าเสื่อมราคาสะสมจนถึงปัจจุบัน')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("depreciated_value_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.depreciated_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("depreciated_value_total_formula"),
                    self.rt_cell_style_decimal]},
            'note': {
                'header': [
                    1, 20, 'text', _render("_('หมายเหตุ')"),
                    None, self.rh_cell_style_center],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render("asset.note")],
                'totals': [1, 0, 'text', None]},
        }

        self.removal_template = {
            'account': {
                'header': [1, 20, 'text', _render("_('รหัส')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'text',
                    _render("asset.number")],
                'totals': [
                    1, 0, 'text', _render("_('รวม')"),
                    None, self.rt_cell_style]},
            'name': {
                'header': [1, 40, 'text', _render("_('ชื่อสินทรัพย์')")],
                'asset_view': [1, 0, 'text', _render("asset.profile_id.name")],
                'asset': [1, 0, 'text', _render("asset.name or ''")],
                'totals': [1, 0, 'text', None]},
            'date_purchase': {
                'header': [1, 20, 'text', _render("_('วันที่ซื้อหรือได้มา')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'date',
                    _render("asset.date_start and "
                            "datetime.strptime(asset.purchase_date,'%Y-%m-%d') "
                            "or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'date_start': {
                'header': [1, 20, 'text', _render("_('วันที่เริ่มคำนวณค่าเสื่อม')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'date',
                    _render("asset.date_start and "
                            "datetime.strptime(asset.date_start,'%Y-%m-%d') "
                            "or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'date_remove': {
                'header': [1, 20, 'text', _render("_('วันที่ตัดจำหน่ายสินทรัพย์')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'date',
                    _render("asset.date_remove and "
                            "datetime.strptime(asset.date_remove,'%Y-%m-%d') "
                            "or None"),
                    None, self.an_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'purchase_value': {
                'header': [
                    1, 18, 'text', _render("_('ราคาทรัพย์สินที่ซื้อหรือได้มา')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("purchase_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.purchase_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("purchase_total_formula"),
                    self.rt_cell_style_decimal]},
            'percent': {
                'header': [
                    1, 18, 'text', _render("_('อัตราร้อยละ')"),
                    None, self.rh_cell_style_right],
                'asset_view': [1, 0, 'text', None],
                'asset': [
                    1, 0, 'number', _render("100.0 / asset.method_number"),
                    None, self.an_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'operating_unit_id': {
                'header': [1, 20, 'text', _render("_('แผนก')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render(
                    "asset.operating_unit_id.code or '-'")],
                'totals': [1, 0, 'text', None]},
            'code': {
                'header': [1, 20, 'text', _render("_('เอกสารอ้างอิง')")],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render("asset.code or ''")],
                'totals': [1, 0, 'text', None]},
            'note': {
                'header': [
                    1, 20, 'text', _render("_('หมายเหตุ')"),
                    None, self.rh_cell_style_center],
                'asset_view': [1, 0, 'text', None],
                'asset': [1, 0, 'text', _render("asset.note")],
                'totals': [1, 0, 'text', None]},
            'depreciation_base': {
                'header': [
                    1, 18, 'text', _render("_('ราคาทรัพย์สินที่ซื้อหรือได้มา')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None,
                    _render("asset_formula"), self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.depreciation_base"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("asset_total_formula"),
                    self.rt_cell_style_decimal]},
            'salvage_value': {
                'header': [
                    1, 18, 'text', _render("_('ราคาซาก')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("salvage_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.salvage_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("salvage_total_formula"),
                    self.rt_cell_style_decimal]},
            'asset_value_previous': {
                'header': [
                    1, 22, 'text', _render("_('มูลค่าต้นทุนในวันสุดท้ายของรอบระยะบัญชีก่อน')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("asset_value_previous_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.asset_value_previous"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("asset_value_previous_total_formula"),
                    self.rt_cell_style_decimal]},
            'remaining_value': {
                'header': [
                    1, 18, 'text', _render("_('มูลค่าต้นทุนหลังจากค่าเสื่อมราคาแล้วจนถึงปัจจุบัน')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("remaining_value_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.remaining_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("remaining_value_total_formula"),
                    self.rt_cell_style_decimal]},
            'asset_line_amount': {
                'header': [
                    1, 22, 'text', _render("_('ค่าเสื่อมราคาที่หักในรอบระยะเวลาบัญชีนี้')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("asset_line_amount_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.asset_line_amount"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("asset_line_amount_total_formula"),
                    self.rt_cell_style_decimal]},
            'depreciated_value': {
                'header': [
                    1, 18, 'text', _render("_('ค่าเสื่อมราคาสะสมจนถึงปัจจุบัน')"),
                    None, self.rh_cell_style_right],
                'asset_view': [
                    1, 0, 'number', None, _render("depreciated_value_formula"),
                    self.av_cell_style_decimal],
                'asset': [
                    1, 0, 'number', _render("asset.depreciated_value"),
                    None, self.an_cell_style_decimal],
                'totals': [
                    1, 0, 'number', None, _render("depreciated_value_total_formula"),
                    self.rt_cell_style_decimal]},
        }

    def _get_title(self, report, format='normal'):
        fy_code = self.fiscalyear.code
        if format == 'short':
            prefix = fy_code
        else:
            prefix = _('Fiscal Year') + ' %s : ' % fy_code
        if report == 'acquisition':
            if format == 'normal':
                suffix = _('New Acquisitions')
            else:
                suffix = '-ACQ'
        elif report == 'active':
            if format == 'normal':
                suffix = _('Active Assets')
            else:
                suffix = '-ACT'
        else:
            if format == 'normal':
                suffix = _('Removed Assets')
            else:
                suffix = '-DSP'
        return prefix + suffix

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

    def _empty_report(self, ws, _p, row_pos, _xs, report):
        cell_style = xlwt.easyxf(_xs['bold'])

        if report == 'acquisition':
            suffix = _('New Acquisitions')
        elif report == 'active':
            suffix = _('Active Assets')
        else:
            suffix = _('Removed Assets')
        no_entries = _("No") + " " + suffix
        c_specs = [
            ('ne', 1, 0, 'text', no_entries),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

    def _get_profile_children(self, profile_id):
        cr = self.cr

        def _child_get(profile_id):
            assets = []
            # SQL in stead of child_ids since ORDER BY different from _order
            cr.execute(
                "SELECT id, type FROM account_asset "
                "WHERE profile_id = %s AND state != 'draft' "
                "ORDER BY date_start ASC, name",
                (profile_id, ))
            children = cr.fetchall()
            for child in children:
                assets.append((child[0], child[1], profile_id))
                assets += _child_get(child[0])
            return assets

        assets = _child_get(profile_id)
        if assets:
            return [(profile_id, 'profile', False)] + assets
        else:
            return []

    def _get_children(self, parent_id):
        cr = self.cr

        def _child_get(asset_id):
            assets = []
            # SQL in stead of child_ids since ORDER BY different from _order
            cr.execute(
                "SELECT id, type FROM account_asset "
                "WHERE parent_id = %s AND state != 'draft' "
                "ORDER BY date_start ASC, name",
                (asset_id, ))
            children = cr.fetchall()
            for child in children:
                assets.append((child[0], child[1], asset_id))
                assets += _child_get(child[0])
            return assets

        assets = _child_get(parent_id)
        return [(parent_id, 'view', False)] + assets

    def _view_add(self, acq, assets):
        parent = filter(lambda x: x[0] == acq[2], self.assets)
        if parent:
            parent = parent[0]
            if parent not in assets:
                self._view_add(parent, assets)
        assets.append(acq)

    def _profile_add(self, acq, assets):
        parent = filter(lambda x: x[0] == acq[2], self.assets)
        if parent:
            parent = parent[0]
            if parent not in assets:
                self._profile_add(parent, assets)
        assets.append(acq)

    def _get_buddha_datetime(self, date):
        date = date.split('-')
        date[0] = str(int(date[0]) + 543)  # year + 543
        date.reverse()
        return '/'.join(date)

    def _acquisition_report(self, _p, _xs, data, objects, wb):
        cr = self.cr
        uid = self.uid
        context = self.context
        if data['period_id']:  # fy will be peroid instead.
            fy = self.pool['account.period'].browse(
                cr, uid, data['period_id'], context=context)
        else:
            fy = self.fiscalyear
        wl_acq = _p.wanted_list_acquisition
        template = self.acquisition_template
        asset_obj = self.pool['account.asset']

        title = self._get_title('acquisition', 'normal')
        title_short = self._get_title('acquisition', 'short')
        sheet_name = title_short[:31].replace('/', '-')
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        start_date = self._get_buddha_datetime(fy.date_start)
        stop_date = self._get_buddha_datetime(fy.date_stop)
        company_id = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        titles = [
            # title,
            company_id.name,
            'รายงานตารางทรัพย์สินที่ซื้อหรือได้มา',
            'ตั้งแต่วันที่ ' + start_date + ' ถึง ' + stop_date,
        ]
        for title in titles:
            row_pos = self._report_title(ws, _p, row_pos, _xs, title, merge=7)
        if not self.asset_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'acquisition')

        cr.execute(
            "SELECT id FROM account_asset "
            "WHERE date_start >= %s AND date_start <= %s"
            "AND id IN %s AND type = 'normal' "
            "ORDER BY date_start ASC",
            (fy.date_start, fy.date_stop, tuple(self.asset_ids)))
        acq_ids = [x[0] for x in cr.fetchall()]

        if not acq_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'acquisition')

        c_specs = map(
            lambda x: self.render(
                x, template, 'header',
                render_space={'_': _p._}),
            wl_acq)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)

        row_pos_start = row_pos
        if 'account' not in wl_acq:
            raise UserError(_('Customization Error'), _(
                "The 'account' field is a mandatory entry of the "
                "'_xls_acquisition_fields' list !"))
        depreciation_base_pos = 'depreciation_base' in wl_acq and \
            wl_acq.index('depreciation_base')
        salvage_value_pos = 'salvage_value' in wl_acq and \
            wl_acq.index('salvage_value')

        acqs = filter(lambda x: x[0] in acq_ids, self.assets)
        acqs_and_parents = []
        for acq in acqs:
            self._profile_add(acq, acqs_and_parents)
        # for acq in acqs:
        #     self._view_add(acq, acqs_and_parents)

        entries = []
        for asset_i, data in enumerate(acqs_and_parents):
            entry = {}
            if data[1] == 'view' or data[1] == 'profile':
                cp_i = asset_i + 1
                cp = []
                for a in acqs_and_parents[cp_i:]:
                    if a[2] == data[0]:
                        cp.append(cp_i)
                    cp_i += 1
                entry['child_pos'] = cp
            if data[1] == 'profile':
                asset_id = asset_obj.search(self.cr, self.uid, [
                    ('profile_id', '=', data[0]),
                ])[0]
                asset = asset_obj.browse(cr, uid, asset_id, context=context)
            else:
                asset = asset_obj.browse(cr, uid, data[0], context=context)
            entry['asset'] = asset
            entries.append(entry)

        asset_formula_cells = []
        salvage_formula_cells = []
        for entry in entries:
            asset = entry['asset']
            if 'child_pos' in entry:  # asset.type == 'view':
                depreciation_base_cells = [
                    rowcol_to_cell(row_pos_start + x, depreciation_base_pos)
                    for x in entry['child_pos']]
                asset_formula = '+'.join(depreciation_base_cells)  # noqa: disable F841, report_xls namespace trick
                asset_formula_cells += depreciation_base_cells
                salvage_value_cells = [
                    rowcol_to_cell(row_pos_start + x, salvage_value_pos)
                    for x in entry['child_pos']]
                salvage_formula = '+'.join(salvage_value_cells)  # noqa: disable F841, report_xls namespace trick
                salvage_formula_cells += salvage_value_cells
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'asset_view'),
                    wl_acq)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.av_cell_style)
            else:
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'asset'),
                    wl_acq)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.an_cell_style)

        asset_total_formula = '+'.join(asset_formula_cells)
        salvage_total_formula = '+'.join(salvage_formula_cells)

        c_specs = map(
            lambda x: self.render(
                x, template, 'totals'),
            wl_acq)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rt_cell_style_right)

    def _active_report(self, _p, _xs, data, objects, wb):
        cr = self.cr
        uid = self.uid
        context = self.context
        if data['period_id']:  # fy will be peroid instead.
            fy = self.pool['account.period'].browse(
                cr, uid, data['period_id'], context=context)
        else:
            fy = self.fiscalyear
        wl_act = _p.wanted_list_active
        template = self.active_template
        asset_obj = self.pool['account.asset']

        title = self._get_title('active', 'normal')
        title_short = self._get_title('active', 'short')
        sheet_name = title_short[:31].replace('/', '-')
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        start_date = self._get_buddha_datetime(fy.date_start)
        stop_date = self._get_buddha_datetime(fy.date_stop)
        company_id = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        titles = [
            # title,
            company_id.name,
            'รายงานตารางค่าเสื่อมราคาสะสม (แนบ ภงด.50)',
            'ตั้งแต่วันที่ ' + start_date + ' ถึง ' + stop_date,
        ]
        for title in titles:
            row_pos = self._report_title(ws, _p, row_pos, _xs, title, merge=14)
        if not self.asset_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'active')

        cr.execute(
            "SELECT id FROM account_asset "
            "WHERE date_start <= %s"
            "AND (date_remove IS NULL OR date_remove >= %s) "
            "AND id IN %s AND type = 'normal' "
            "ORDER BY date_start ASC",
            (fy.date_stop, fy.date_start, tuple(self.asset_ids))
        )
        act_ids = [x[0] for x in cr.fetchall()]

        if not act_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'active')

        # filter only asset that run asset_line in period
        cr.execute(
            "SELECT asset_id FROM account_asset_line "
            "WHERE move_check = true "
            "AND type = 'depreciate' "
            "AND line_date >= %s "
            "AND asset_id in %s ",
            (fy.date_start, tuple(act_ids))
        )
        act_ids = [x[0] for x in cr.fetchall()]

        if not act_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'active')

        c_specs = map(
            lambda x: self.render(
                x, template, 'header',
                render_space={'_': _p._}),
            wl_act)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)

        row_pos_start = row_pos
        if 'account' not in wl_act:
            raise UserError(_('Customization Error'), _(
                "The 'account' field is a mandatory entry of the "
                "'_xls_active_fields' list !"))
        depreciation_base_pos = 'depreciation_base' in wl_act and \
            wl_act.index('depreciation_base')
        salvage_value_pos = 'salvage_value' in wl_act and \
            wl_act.index('salvage_value')
        fy_start_value_pos = 'fy_start_value' in wl_act and \
            wl_act.index('fy_start_value')
        fy_end_value_pos = 'fy_end_value' in wl_act and \
            wl_act.index('fy_end_value')
        purchase_value_pos = 'purchase_value' in wl_act and \
            wl_act.index('purchase_value')
        asset_line_amount_pos = 'asset_line_amount' in wl_act and \
            wl_act.index('asset_line_amount')
        value_residual_pos = 'residual_value' in wl_act and \
            wl_act.index('residual_value')
        asset_value_previous_pos = 'asset_value_previous' in wl_act and \
            wl_act.index('asset_value_previous')
        depreciated_value_pos = 'depreciated_value' in wl_act and \
            wl_act.index('depreciated_value')
        remaining_value_pos = 'remaining_value' in wl_act and \
            wl_act.index('remaining_value')

        acts = filter(lambda x: x[0] in act_ids, self.assets)
        acts_and_parents = []
        # for act in acts:
        #     self._view_add(act, acts_and_parents)
        for act in acts:
            self._profile_add(act, acts_and_parents)

        entries = []
        for asset_i, data in enumerate(acts_and_parents):
            entry = {}
            # asset = asset_obj.browse(cr, uid, data[0], context=context)
            if data[1] == 'profile':
                asset_id = asset_obj.search(self.cr, self.uid, [
                    ('profile_id', '=', data[0]),
                ])[0]
                asset = asset_obj.browse(cr, uid, asset_id, context=context)
            else:
                asset = asset_obj.browse(cr, uid, data[0], context=context)

            if data[1] == 'view' or data[1] == 'profile':
                cp_i = asset_i + 1
                cp = []
                for a in acts_and_parents[cp_i:]:
                    if a[2] == data[0]:
                        cp.append(cp_i)
                    cp_i += 1
                entry['child_pos'] = cp

            else:

                # fy_start_value, depreciated_value
                cr.execute(
                    "SELECT depreciated_value "
                    "FROM account_asset_line "
                    "WHERE line_date >= %s"
                    "AND asset_id = %s AND type = 'depreciate' "
                    "ORDER BY line_date ASC LIMIT 1",
                    (fy.date_start, data[0]))
                res = cr.fetchone()
                if res:
                    value_depreciated = res[0]
                elif asset.state in ['close', 'removed']:
                    value_depreciated = asset.value_depreciated
                elif not asset.method_number:
                    value_depreciated = 0.0
                else:
                    error_name = asset.name
                    if asset.code:
                        error_name += ' (' + asset.code + ')' or ''
                    if asset.state in ['open']:
                        cr.execute(
                            "SELECT line_date "
                            "FROM account_asset_line "
                            "WHERE asset_id = %s AND type = 'depreciate' "
                            "AND init_entry=FALSE AND move_check=FALSE "
                            "AND line_date < %s"
                            "ORDER BY line_date ASC LIMIT 1",
                            (data[0], fy.date_start))
                        res = cr.fetchone()
                        if res:
                            raise UserError(
                                _('Data Error'),
                                _("You can not report on a Fiscal Year "
                                  "with unposted entries in prior years. "
                                  "Please post depreciation table entry "
                                  "dd. '%s'  of asset '%s' !")
                                % (res[0], error_name))
                        else:
                            raise UserError(
                                _('Data Error'),
                                _("Depreciation Table error for asset %s !")
                                % error_name)
                    else:
                        raise UserError(
                            _('Data Error'),
                            _("Depreciation Table error for asset %s !")
                            % error_name)
                asset.fy_start_value = \
                    asset.depreciation_base - value_depreciated

                # fy_end_value
                cr.execute(
                    "SELECT depreciated_value "
                    "FROM account_asset_line "
                    "WHERE line_date > %s"
                    "AND asset_id = %s AND type = 'depreciate' "
                    "ORDER BY line_date ASC LIMIT 1",
                    (fy.date_stop, data[0]))
                res = cr.fetchone()
                if res:
                    value_depreciated = res[0]
                elif not asset.method_number:
                    value_depreciated = 0.0
                else:
                    value_depreciated = asset.depreciation_base
                asset.fy_end_value = \
                    asset.depreciation_base - value_depreciated

                # depreciation line amount
                cr.execute(
                    "SELECT amount, remaining_value, depreciated_value "
                    "FROM account_asset_line "
                    "WHERE line_date <= %s AND "
                    "asset_id = %s AND type = 'depreciate' "
                    "AND move_check=true "
                    "ORDER BY line_date DESC LIMIT 1",
                    (fy.date_stop, data[0]))
                res = cr.fetchone()
                if res:
                    value_line_amount = res[0]
                    value_line_previous = res[0] + res[1]
                    value_line_remaining = res[1]
                    value_line_depreciated = res[0] + res[2]
                else:
                    value_line_amount = asset.depreciation_base
                    value_line_previous = \
                        value_line_amount + asset.value_residual
                    value_line_remaining = asset.value_residual
                    value_line_depreciated = asset.value_depreciated
                asset.asset_line_amount = value_line_amount
                asset.asset_value_previous = value_line_previous
                asset.remaining_value = value_line_remaining
                asset.depreciated_value = value_line_depreciated
            entry['asset'] = asset
            entries.append(entry)

        purchase_formula_cells = []
        asset_line_amount_formula_cells = []
        value_residual_formula_cells = []
        asset_value_previous_formula_cells = []
        depreciated_value_formula_cells = []
        remaining_value_formula_cells = []
        salvage_formula_cells = []
        for entry in entries:
            asset = entry['asset']

            fy_start_value_cell = rowcol_to_cell(row_pos, fy_start_value_pos)
            fy_end_value_cell = rowcol_to_cell(row_pos, fy_end_value_pos)
            depreciation_base_cell = rowcol_to_cell(
                row_pos, depreciation_base_pos)
            fy_diff_formula = fy_start_value_cell + '-' + fy_end_value_cell
            total_depr_formula = depreciation_base_cell \
                + '-' + fy_end_value_cell

            if 'child_pos' in entry:  # asset.type == 'view':

                depreciation_base_cells = [
                    rowcol_to_cell(row_pos_start + x, depreciation_base_pos)
                    for x in entry['child_pos']]
                asset_formula = '+'.join(depreciation_base_cells)  # noqa: disable F841, report_xls namespace trick

                salvage_value_cells = [
                    rowcol_to_cell(row_pos_start + x, salvage_value_pos)
                    for x in entry['child_pos']]
                salvage_formula = '+'.join(salvage_value_cells)  # noqa: disable F841, report_xls namespace trick
                salvage_formula_cells += salvage_value_cells

                fy_start_value_cells = [
                    rowcol_to_cell(row_pos_start + x, fy_start_value_pos)
                    for x in entry['child_pos']]
                fy_start_formula = '+'.join(fy_start_value_cells)  # noqa: disable F841, report_xls namespace trick

                fy_end_value_cells = [
                    rowcol_to_cell(row_pos_start + x, fy_end_value_pos)
                    for x in entry['child_pos']]
                fy_end_formula = '+'.join(fy_end_value_cells)  # noqa: disable F841, report_xls namespace trick
                purchase_value_cells = [
                    rowcol_to_cell(row_pos_start + x, purchase_value_pos)
                    for x in entry['child_pos']
                ]
                purchase_formula = '+'.join(purchase_value_cells)
                purchase_formula_cells += purchase_value_cells

                asset_line_amount_calls = [
                    rowcol_to_cell(row_pos_start + x, asset_line_amount_pos)
                    for x in entry['child_pos']
                ]
                asset_line_amount_formula = '+'.join(asset_line_amount_calls)
                asset_line_amount_formula_cells += asset_line_amount_calls

                value_residual_cells = [
                    rowcol_to_cell(row_pos_start + x, value_residual_pos)
                    for x in entry['child_pos']
                ]
                value_residual_formula = '+'.join(value_residual_cells)
                value_residual_formula_cells += value_residual_cells

                asset_value_previous_cells = [
                    rowcol_to_cell(row_pos_start + x, asset_value_previous_pos)
                    for x in entry['child_pos']
                ]
                asset_value_previous_formula = '+'.join(asset_value_previous_cells)
                asset_value_previous_formula_cells += asset_value_previous_cells

                depreciated_value_cells = [
                    rowcol_to_cell(row_pos_start + x, depreciated_value_pos)
                    for x in entry['child_pos']
                ]
                depreciated_value_formula = '+'.join(depreciated_value_cells)
                depreciated_value_formula_cells += depreciated_value_cells

                remaining_value_cells = [
                    rowcol_to_cell(row_pos_start + x, remaining_value_pos)
                    for x in entry['child_pos']
                ]
                remaining_value_formula = '+'.join(remaining_value_cells)
                remaining_value_formula_cells += remaining_value_cells
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'asset_view'),
                    wl_act)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.av_cell_style)

            else:
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'asset'),
                    wl_act)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.an_cell_style)

        asset_total_formula = rowcol_to_cell(row_pos_start, depreciation_base_pos)  # noqa: disable F841, report_xls namespace trick
        salvage_total_formula = '+'.join(salvage_formula_cells)
        fy_start_total_formula = rowcol_to_cell(row_pos_start,  # noqa: disable F841, report_xls namespace trick
                                                fy_start_value_pos)
        fy_end_total_formula = rowcol_to_cell(row_pos_start, fy_end_value_pos)  # noqa: disable F841, report_xls namespace trick

        fy_start_value_cell = rowcol_to_cell(row_pos, fy_start_value_pos)
        fy_end_value_cell = rowcol_to_cell(row_pos, fy_end_value_pos)
        depreciation_base_cell = rowcol_to_cell(row_pos, depreciation_base_pos)
        fy_diff_formula = fy_start_value_cell + '-' + fy_end_value_cell  # noqa: disable F841, report_xls namespace trick
        total_depr_formula = depreciation_base_cell + '-' + fy_end_value_cell  # noqa: disable F841, report_xls namespace trick

        purchase_total_formula = '+'.join(purchase_formula_cells)
        asset_line_amount_total_formula = '+'.join(
            asset_line_amount_formula_cells)
        value_residual_total_formula = '+'.join(value_residual_formula_cells)
        asset_value_previous_total_formula = '+'.join(
            asset_value_previous_formula_cells)
        depreciated_value_total_formula = '+'.join(
            depreciated_value_formula_cells)
        remaining_value_total_formula = '+'.join(remaining_value_formula_cells)

        c_specs = map(
            lambda x: self.render(
                x, template, 'totals'),
            wl_act)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rt_cell_style_right)

    def _removal_report(self, _p, _xs, data, objects, wb):
        cr = self.cr
        uid = self.uid
        context = self.context
        if data['period_id']:  # fy will be peroid instead.
            fy = self.pool['account.period'].browse(
                cr, uid, data['period_id'], context=context)
        else:
            fy = self.fiscalyear
        wl_dsp = _p.wanted_list_removal
        template = self.removal_template
        asset_obj = self.pool['account.asset']

        title = self._get_title('removal', 'normal')
        title_short = self._get_title('removal', 'short')
        sheet_name = title_short[:31].replace('/', '-')
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        start_date = self._get_buddha_datetime(fy.date_start)
        stop_date = self._get_buddha_datetime(fy.date_stop)

        company_id = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        titles = [
            # title,
            company_id.name,
            'รายงานตารางค่าเสื่อมราคาสะสม (แนบ ภงด.50)',
            'ตั้งแต่วันที่ ' + start_date + ' ถึง ' + stop_date,
        ]
        for title in titles:
            row_pos = self._report_title(ws, _p, row_pos, _xs, title, merge=15)
        if not self.asset_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'removal')

        cr.execute(
            "SELECT id FROM account_asset "
            "WHERE date_remove >= %s AND date_remove <= %s"
            "AND id IN %s AND type = 'normal' "
            "ORDER BY date_remove ASC",
            (fy.date_start, fy.date_stop, tuple(self.asset_ids)))
        dsp_ids = [x[0] for x in cr.fetchall()]

        if not dsp_ids:
            return self._empty_report(ws, _p, row_pos, _xs, 'removal')

        c_specs = map(
            lambda x: self.render(
                x, template, 'header',
                render_space={'_': _p._}),
            wl_dsp)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)

        row_pos_start = row_pos
        if 'account' not in wl_dsp:
            raise UserError(_('Customization Error'), _(
                "The 'account' field is a mandatory entry of the "
                "'_xls_removal_fields' list !"))
        depreciation_base_pos = 'depreciation_base' in wl_dsp and \
            wl_dsp.index('depreciation_base')
        salvage_value_pos = 'salvage_value' in wl_dsp and \
            wl_dsp.index('salvage_value')
        purchase_value_pos = 'purchase_value' in wl_dsp and \
            wl_dsp.index('purchase_value')
        asset_line_amount_pos = 'asset_line_amount' in wl_dsp and \
            wl_dsp.index('asset_line_amount')
        asset_value_previous_pos = 'asset_value_previous' in wl_dsp and \
            wl_dsp.index('asset_value_previous')
        depreciated_value_pos = 'depreciated_value' in wl_dsp and \
            wl_dsp.index('depreciated_value')
        remaining_value_pos = 'remaining_value' in wl_dsp and \
            wl_dsp.index('remaining_value')

        dsps = filter(lambda x: x[0] in dsp_ids, self.assets)
        dsps_and_parents = []
        # for dsp in dsps:
        #     self._view_add(dsp, dsps_and_parents)
        for dsp in dsps:
            self._profile_add(dsp, dsps_and_parents)

        entries = []
        for asset_i, data in enumerate(dsps_and_parents):
            entry = {}
            # asset = asset_obj.browse(cr, uid, data[0], context=context)
            if data[1] == 'profile':
                asset_id = asset_obj.search(self.cr, self.uid, [
                    ('profile_id', '=', data[0]),
                ])[0]
                asset = asset_obj.browse(cr, uid, asset_id, context=context)
            else:
                asset = asset_obj.browse(cr, uid, data[0], context=context)
            if data[1] == 'view' or data[1] == 'profile':
                cp_i = asset_i + 1
                cp = []
                for a in dsps_and_parents[cp_i:]:
                    if a[2] == data[0]:
                        cp.append(cp_i)
                    cp_i += 1
                entry['child_pos'] = cp
            else:
                # depreciation line amount
                cr.execute(
                    "SELECT amount, remaining_value, depreciated_value "
                    "FROM account_asset_line "
                    "WHERE line_date <= %s AND "
                    "asset_id = %s AND type = 'remove' "
                    "AND move_check=true "
                    "ORDER BY line_date DESC LIMIT 1",
                    (fy.date_stop, data[0]))
                res = cr.fetchone()
                if res:
                    value_line_amount = res[2]
                    value_line_previous = res[0] + res[1]
                    value_line_remaining = res[1]
                    value_line_depreciated = asset.value_depreciated - res[0]
                else:
                    value_line_amount = asset.depreciation_base
                    value_line_previous = \
                        value_line_amount + asset.value_residual
                    value_line_remaining = asset.value_residual
                    value_line_depreciated = asset.value_depreciated
                asset.asset_line_amount = value_line_amount
                asset.asset_value_previous = value_line_previous
                asset.remaining_value = value_line_remaining
                asset.depreciated_value = value_line_depreciated
            entry['asset'] = asset
            entries.append(entry)

        asset_formula_cells = []
        salvage_formula_cells = []
        purchase_formula_cells = []
        asset_line_amount_formula_cells = []
        asset_value_previous_formula_cells = []
        depreciated_value_formula_cells = []
        remaining_value_formula_cells = []
        for entry in entries:
            asset = entry['asset']
            if 'child_pos' in entry:  # asset.type == 'view':
                depreciation_base_cells = [
                    rowcol_to_cell(row_pos_start + x, depreciation_base_pos)
                    for x in entry['child_pos']]
                asset_formula = '+'.join(depreciation_base_cells)  # noqa: disable F841, report_xls namespace trick
                asset_formula_cells += depreciation_base_cells

                salvage_value_cells = [
                    rowcol_to_cell(row_pos_start + x, salvage_value_pos)
                    for x in entry['child_pos']]
                salvage_formula = '+'.join(salvage_value_cells)  # noqa: disable F841, report_xls namespace trick
                salvage_formula_cells += salvage_value_cells

                purchase_value_cells = [
                    rowcol_to_cell(row_pos_start + x, purchase_value_pos)
                    for x in entry['child_pos']
                ]
                purchase_formula = '+'.join(purchase_value_cells)
                purchase_formula_cells += purchase_value_cells

                asset_line_amount_calls = [
                    rowcol_to_cell(row_pos_start + x, asset_line_amount_pos)
                    for x in entry['child_pos']
                ]
                asset_line_amount_formula = '+'.join(asset_line_amount_calls)
                asset_line_amount_formula_cells += asset_line_amount_calls

                asset_value_previous_cells = [
                    rowcol_to_cell(row_pos_start + x, asset_value_previous_pos)
                    for x in entry['child_pos']
                ]
                asset_value_previous_formula = '+'.join(asset_value_previous_cells)
                asset_value_previous_formula_cells += asset_value_previous_cells

                depreciated_value_cells = [
                    rowcol_to_cell(row_pos_start + x, depreciated_value_pos)
                    for x in entry['child_pos']
                ]
                depreciated_value_formula = '+'.join(depreciated_value_cells)
                depreciated_value_formula_cells += depreciated_value_cells

                remaining_value_cells = [
                    rowcol_to_cell(row_pos_start + x, remaining_value_pos)
                    for x in entry['child_pos']
                ]
                remaining_value_formula = '+'.join(remaining_value_cells)
                remaining_value_formula_cells += remaining_value_cells
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'asset_view'),
                    wl_dsp)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.av_cell_style)
            else:
                c_specs = map(
                    lambda x: self.render(
                        x, template, 'asset'),
                    wl_dsp)
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.an_cell_style)

        asset_total_formula = '+'.join(asset_formula_cells)
        salvage_total_formula = '+'.join(salvage_formula_cells)
        purchase_total_formula = '+'.join(purchase_formula_cells)
        asset_line_amount_total_formula = '+'.join(
            asset_line_amount_formula_cells)
        asset_value_previous_total_formula = '+'.join(
            asset_value_previous_formula_cells)
        depreciated_value_total_formula = '+'.join(
            depreciated_value_formula_cells)
        remaining_value_total_formula = '+'.join(remaining_value_formula_cells)

        c_specs = map(
            lambda x: self.render(
                x, template, 'totals'),
            wl_dsp)
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rt_cell_style_right)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        wl_act = _p.wanted_list_active  # noqa: disable F841, report_xls namespace trick
        wl_rem = _p.wanted_list_removal  # noqa: disable F841, report_xls namespace trick
        self.acquisition_template.update(_p.template_update_acquisition)
        self.active_template.update(_p.template_update_active)
        self.removal_template.update(_p.template_update_removal)
        fy = self.pool.get('account.fiscalyear').browse(
            self.cr, self.uid, data['fiscalyear_id'], context=self.context)
        self.fiscalyear = fy

        profile_obj = self.pool.get('account.asset.profile')
        if data['profile_ids']:
            self.profiles = profile_obj.search(self.cr, self.uid, [
                ('id', 'in', data['profile_ids']),
            ])
        else:
            self.profiles = profile_obj.search(self.cr, self.uid, [])
        asset_objects = []
        for profile_id in self.profiles:
            asset_objects += self._get_profile_children(profile_id)
        self.assets = asset_objects
        self.asset_ids = [
            x[0] for x in filter(lambda r: r[1] == u'normal', self.assets)]
        # self.assets = self._get_children(objects[0].id)
        # self.asset_ids = [x[0] for x in self.assets]
        self._acquisition_report(_p, _xs, data, objects, wb)
        self._active_report(_p, _xs, data, objects, wb)
        self._removal_report(_p, _xs, data, objects, wb)


AssetReportXls(
    'report.account.depreciation.xls',
    'account.asset',
    parser=AssetReportXlsParser)
