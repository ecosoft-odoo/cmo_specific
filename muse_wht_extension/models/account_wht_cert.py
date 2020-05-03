# -*- coding: utf-8 -*-

from openerp import models, api


class AccountWhtCert(models.Model):
    _inherit = "account.wht.cert"

    @api.multi
    def _assign_number(self):
        """ PND1: XSMSYY, PND3: XPMSYY, PND53: XCMSYY """
        tax_forms = {"pnd1": "XSMS",
                     "pnd3": "XPMS",
                     "pnd53": "XCMS"}
        super(AccountWhtCert, self)._assign_number()
        for cert in self:
            if cert.sequence:
                fy = cert.rpt_period_id.fiscalyear_id.code
                cert.number = "%s%s-%s" % (tax_forms[cert.income_tax_form],
                                           fy, cert.sequence_display)