# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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

from osv import osv, fields
from tools.translate import _

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'no_quality': fields.boolean('Scont')
    }
    
    def action_move_create(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.no_quality and not inv.journal_id.no_quality:
                raise osv.except_osv(_('Error !'), _('You try to open scont invoice on not scont journal.'))
            elif not inv.no_quality and inv.journal_id.no_quality:
                raise osv.except_osv(_('Error !'), _('You try to open normal invoice on scont journal.'))
            
        return super(account_invoice, self).action_move_create(cr, uid, ids, context)
        
    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        res = super(account_invoice, self).create(cr, uid, vals, context=context)
        if vals.get('no_quality', False):
            obj = self.browse(cr, uid, res)
            if obj.invoice_line:
                self.pool.get('account.invoice.line').write(cr, uid, [x.id for x in obj.invoice_line], {
                                                                'invoice_line_tax_id': [(6,0, [])],
                                                            })
            if obj.tax_line:
                self.pool.get('account.invoice.tax').unlink(cr, uid, [x.id for x in obj.tax_line])
        
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if isinstance(ids, (int, long)): ids = [ids]
        
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        
        if vals.get('no_quality', False):
            for invoice in self.browse(cr, uid, ids):
                if invoice.invoice_line:
                    self.pool.get('account.invoice.line').write(cr, uid, [x.id for x in invoice.invoice_line], {
                                                                'invoice_line_tax_id': [(6,0, [])],
                                                            })
                if invoice.tax_line:
                    self.pool.get('account.invoice.tax').unlink(cr, uid, [x.id for x in invoice.tax_line])
                                                            
        return res

account_invoice()
