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

from openerp.osv import osv, fields
import time
import calendar

class contract_to_invoice(osv.osv_memory):
    
    _name = "contract.to_invoice"
    
    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')

        vals = []

        value = journal_obj.search(cr, uid, [('type', '=','sale' )])
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            t1 = jr_type.id,jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),
        'invoice_date': fields.date('Invoiced date', required=True),
        'invoice_date_to': fields.date('Invoice to', required=True)
    }
    
    _defaults = {
        'invoice_date': lambda *a: time.strftime("%Y-%m-%d"),
        'invoice_date_to': lambda *a: time.strftime("%Y-%m-") + str(calendar.monthrange(int(time.strftime('%Y')), int(time.strftime('%m')))[1])
    }
    
    def action_invoice(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res = {}
        obj = self.browse(cr, uid, ids[0])
        if context.get('active_ids', []):
            context['invoice_date'] = obj.invoice_date
            context['journal_id'] = obj.journal_id
            context['end_date'] = obj.invoice_date_to
            res = self.pool.get('account.analytic.account').invoice_run(cr, uid, context['active_ids'], context=context)
            if isinstance(res, dict):
                del res["nodestroy"]
            else:
                res = {}
        return res
    
contract_to_invoice()
