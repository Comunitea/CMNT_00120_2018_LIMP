# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from openerp import models, fields, orm
from tools.translate import _


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    _columns= {
               'origin': fields.char('Source Document', size=500, help="Reference of the document that produced this invoice.", readonly=True, states={'draft':[('readonly',False)]}),
               }
    def action_move_create(self, cr, uid, ids, *args):
        context = args
        for invoice in self.browse(cr, uid, ids, context):
            if not invoice.type in ('in_invoice','in_refund'):
                continue
            domain = []
            domain.append( ('partner_id','=',invoice.partner_id.id) )
            domain.append( ('type','=',invoice.type) )
            domain.append( ('date_invoice', '=', invoice.date_invoice) )
            domain.append( ('reference', '=', invoice.reference) )
            domain.append( ('state','in', ('open','paid','unpaid')) )
            invoice_ids = self.search(cr, uid, domain, context=context)
            if len(invoice_ids) > 1:
                text = []
                for invoice in self.browse(cr, uid, invoice_ids, context):
                    text.append( _('Partner: %s\nInvoice Reference: %s') % ( invoice.partner_id.name, invoice.reference ) )
                text = '\n\n'.join( text )
                raise osv.except_osv( _('Validation Error'), _('The following supplier invoices have duplicated information:\n\n%s') % text)
        ret = super(account_invoice, self).action_move_create(cr, uid, ids, *args)
        return ret
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = {}
        journal = False
        if context.has_key('journal_type'):
            journal = context['journal_type']
            if isinstance(journal,(str, unicode)):
                journal=[journal]
            if len(journal) == 1:
                res = super(account_invoice, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
            else:
                journal_obj = self.pool.get('account.journal')
                if context is None:
                    context = {}

                if context.get('active_model', '') in ['res.partner'] and context.get('active_ids', False) and context['active_ids']:
                    partner = self.pool.get(context['active_model']).read(cr, uid, context['active_ids'], ['supplier','customer'])[0]
                    if not view_type:
                        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'account.invoice.tree')])
                        view_type = 'tree'
                    if view_type == 'form':
                        if partner['supplier'] and not partner['customer']:
                            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', 'account.invoice.supplier.form')])
                        else:
                            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', 'account.invoice.form')])
                if view_id and isinstance(view_id, (list, tuple)):
                    view_id = view_id[0]
                res = super(account_invoice,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

                type = context.get('journal_type', 'sale')
                for field in res['fields']:
                    if field == 'journal_id':
                        journal_select = journal_obj._name_search(cr, uid, '', [('type', 'in', type)], context=context, limit=None, name_get_uid=1)
                        res['fields'][field]['selection'] = journal_select

                if view_type == 'tree':
                    doc = etree.XML(res['arch'])
                    nodes = doc.xpath("//field[@name='partner_id']")
                    partner_string = _('Customer')
                    if context.get('type', 'out_invoice') in ('in_invoice', 'in_refund'):
                        partner_string = _('Supplier')
                    for node in nodes:
                        node.set('string', partner_string)
                    res['arch'] = etree.tostring(doc)
        else:
            res = super(account_invoice, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res


account_invoice()

class account_invoice_refund(models.TransientModel):

    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        journal_obj = self.pool.get('account.journal')
        res = super(account_invoice_refund,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('journal_type', 'sale_refund')
        if type in ('sale', 'sale_refund'):
            type = 'sale_refund'
        elif type[0] in ('sale', 'sale_refund'):
            type = 'sale_refund'
        else:
            type = 'purchase_refund'
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(cr, uid, '', [('type', '=', type)], context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
        return res

account_invoice_refund()
