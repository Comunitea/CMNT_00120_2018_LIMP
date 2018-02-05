# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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

from openerp import models, fields

class stock_invoice_onshipping(models.TransientModel):
    
    _inherit = "stock.invoice.onshipping"
    
    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}

        model = context.get('active_model')
        if not model or model != 'stock.picking':
            return []
            
        journal_obj = self.pool.get('account.journal')
        vals = []
                     
        value = journal_obj.search(cr, uid, [('type', 'in', ['purchase_refund','sale','purchase','sale_refund'])])
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            t1 = jr_type.id,jr_type.name
            vals.append(t1)
        return vals
        
    def _get_default_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
            
        model = context.get('active_model')
        if not model or model != 'stock.picking':
            return False
            
        model_pool = self.pool.get(model)
        journal_obj = self.pool.get('account.journal')
        res_ids = context and context.get('active_ids', [])
        vals = []
        browse_picking = model_pool.browse(cr, uid, res_ids, context=context)
        journal_id = False
        
        for pick in browse_picking:
            src_usage = pick.move_lines[0].location_id.usage
            dest_usage = pick.move_lines[0].location_dest_id.usage
            type = pick.type
            if pick.from_spicking and type == 'in':
                journal_type = 'sale'
            elif type == 'out' and dest_usage == 'supplier':
                journal_type = 'purchase_refund'
            elif type == 'out' and dest_usage == 'customer':
                journal_type = 'sale'
            elif type == 'in' and src_usage == 'supplier':
                journal_type = 'purchase'
            elif type == 'in' and src_usage == 'customer':
                journal_type = 'sale_refund'
            else:
                journal_type = 'sale'
                
            journal_id = journal_obj.search(cr, uid, [('type', '=',journal_type)])
            
        return journal_id
    
    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),
    }
    
    _defaults = {
        'journal_id': _get_default_journal
    }
    
    
stock_invoice_onshipping()
