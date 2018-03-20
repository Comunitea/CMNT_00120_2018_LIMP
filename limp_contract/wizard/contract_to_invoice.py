# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api
import time
import calendar

class ContractToInvoice(models.TransientModel):

    _name = "contract.to_invoice"


    @api.model
    def _get_journal_id(self):
        vals = []
        value = self.env['account.journal'].search([('type', '=', 'sale')])
        for jr_type in value:
            t1 = jr_type.id, jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    @api.model
    def _default_invoice_date_to(self):
        time.strftime("%Y-%m-") + \
            str(calendar.monthrange(
                int(time.strftime('%Y')), int(time.strftime('%m')))[1])

    journal_id = fields.Selection(_get_journal_id, 'Destination Journal',
                                  required=True)
    invoice_date = fields.Date('Invoiced date', required=True,
                               default=fields.Date.today)
    invoice_date_to = fields.Date('Invoice to', required=True,
                                  default=_default_invoice_date_to)

    def action_invoice(self):
        res = {}
        if self._context.get('active_model', False) == 'limp.contract' and self._context.get('active_ids', []):
            ctx = dict(self._context)
            context['invoice_date'] = self.invoice_date
            context['journal_id'] = self.journal_id
            context['end_date'] = self.invoice_date_to
            res = self.env['limp.contract'].invoice_run(context['active_ids'])
            if isinstance(res, dict):
                del res["nodestroy"]
            else:
                res = {}
        return res
