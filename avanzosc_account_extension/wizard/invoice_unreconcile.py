# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2012 Avanzosc <http://www.avanzosc.com>
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

class invoice_unreconcile(osv.osv_memory):

    _name = 'invoice.unreconcile'

    def unreconcile_invoices(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('account.move.line')
        invoice_ids =  context.get('active_ids',[])
        inv_ids = inv_obj.browse(cr,uid, invoice_ids)
        toreturn_moves = {}

        if inv_ids:
            for inv in inv_ids:
                toreturn_moves[inv.id] = []
                for pay_id in inv.payment_ids:
                    toreturn_moves[inv.id].append(pay_id)

                move = move_obj.browse(cr, uid, inv.move_id.id)
                for line in move.line_id:
                    if line.reconcile_id:
                        line_obj._remove_move_reconcile(cr, uid, [line.id])

        if toreturn_moves:
            date = time.strftime('%Y-%m-%d')
            period_ids = self.pool.get('account.period').find(cr, uid, date, context)
            period_id = period_ids and period_ids[0] or False

            for return_move in toreturn_moves:
                inv = self.pool.get('account.invoice').browse(cr, uid, return_move)
                move_id = self.pool.get('account.move').create(cr, uid, {
                    'ref': _("Refund: ") + inv.number,
                    'journal_id': toreturn_moves[return_move][0].journal_id.id,
                    'period_id': period_id,
                    'date': date,
                })
                invoice_line_id = False
                for move_line in toreturn_moves[return_move]:
                    vals = {
                        'name': move_line.name,
                        'ref': _("Refund: ") + (move_line.ref or inv.number),
                        'product_id': move_line.product_id.id,
                        'account_id': move_line.account_id.id,
                        'debit': move_line.credit,
                        'credit': move_line.debit,
                        'quantity': move_line.quantity,
                        'move_id': move_id,
                        'journal_id': move_line.journal_id.id,
                        'period_id': period_id,
                        'date': date,
                        'partner_id': move_line.partner_id.id
                    }
                    new_move_line = self.pool.get('account.move.line').create(cr, uid, vals)
                    if move_line.account_id.id == inv.account_id.id:
                        invoice_line_id = new_move_line
                    vals2 = {
                       'name': move_line.name,
                        'ref': _("Refund: ") + (move_line.ref or inv.number),
                        'product_id': move_line.product_id.id,
                        'account_id': move_line.journal_id.default_debit_account_id.id,
                        'debit': move_line.debit,
                        'credit': move_line.credit,
                        'quantity': move_line.quantity,
                        'move_id': move_id,
                        'journal_id': move_line.journal_id.id,
                        'period_id': period_id,
                        'date': date,
                        'partner_id': move_line.partner_id.id
                    }
                    self.pool.get('account.move.line').create(cr, uid, vals2)

                self.pool.get('account.move').post(cr, uid, [move_id])
                self.pool.get('account.move.line').reconcile(cr, uid, [toreturn_moves[return_move][0].id,invoice_line_id])

        return {'type': 'ir.actions.act_window.close()'}

invoice_unreconcile()
