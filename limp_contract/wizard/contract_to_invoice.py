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

class contract_to_invoice(osv.osv_memory):
    
    _inherit = "contract.to_invoice"
    
    def action_invoice(self, cr, uid, ids, context=None):
        if context is None: context = {}
        
        if context.get('active_model', False) == 'limp.contract':
            res = {}
            obj = self.browse(cr, uid, ids[0])
            if context.get('active_ids', []):
                context['invoice_date'] = obj.invoice_date
                context['journal_id'] = obj.journal_id
                context['end_date'] = obj.invoice_date_to
                res = self.pool.get('limp.contract').invoice_run(cr, uid, context['active_ids'], context=context)
                if isinstance(res, dict):
                    del res["nodestroy"]
                else:
                    res = {}
        else:
            res = super(contract_to_invoice, self).action_invoice(cr, uid, ids, context=context)
            
        return res
    
contract_to_invoice()
