# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PrintWhtCertWizard(models.TransientModel):
    _inherit = 'print.wht.cert.wizard'

    @api.multi
    def run_report(self):
        data = {'parameters': {}}
        form_data = self._get_form_data()
        data['parameters'] = form_data
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_cmo_withholding_cert',
            'datas': data,
            'context': {'lang': 'th_TH'},
        }
        return res
