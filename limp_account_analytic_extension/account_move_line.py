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

class account_move_line(osv.osv):

    _inherit = "account.move.line"

    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'manager_id': fields.many2one('hr.employee', 'Responsible', domain=[('responsible', '=', True)])
    }

    _defaults = {
        'department_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).context_department_id.id,
        'delegation_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).context_delegation_id.id,
        'manager_id': lambda self, cr, uid, context: self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0] or False,
    }

    def create_analytic_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        analytic_line_obj = self.pool.get('account.analytic.line')
        for line in self.browse(cr, uid, ids, context=context):
            toremove = analytic_line_obj.search(cr, uid, [('move_id','=',line.id)], context=context)
            if toremove:
                analytic_line_obj.unlink(cr, uid, toremove, context=context)
            if line.analytic_account_id:
                if not line.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal !'),_("You have to define an analytic journal on the '%s' journal!") % (line.journal_id.name, ))
                amt = (line.credit or  0.0) - (line.debit or 0.0)
                vals_lines = {
                    'name': line.name,
                    'date': line.date,
                    'account_id': line.analytic_account_id.id,
                    'unit_amount': line.quantity,
                    'product_id': line.product_id and line.product_id.id or False,
                    'product_uom_id': line.product_uom_id and line.product_uom_id.id or False,
                    'amount': amt,
                    'general_account_id': line.account_id.id,
                    'journal_id': line.journal_id.analytic_journal_id.id,
                    'ref': line.ref,
                    'move_id': line.id,
                    'user_id': uid,
                    'department_id': line.department_id and line.department_id.id or False,
                    'delegation_id': line.delegation_id and line.delegation_id.id or False,
                    'manager_id': line.manager_id and line.manager_id.id or False,
                    'partner_id': line.move_id and line.move_id.partner_id and line.move_id.partner_id.id or False,
                }
                if line.invoice:
                    vals_lines.update({'department_id': line.invoice.department_id.id,
                                        'delegation_id': line.invoice.delegation_id.id,
                                        'manager_id': line.invoice.manager_id.id})
                c = analytic_line_obj.create(cr, uid, vals_lines)
            elif line.analytics_id:
                if not line.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal !'),_("You have to define an analytic journal on the '%s' journal!") % (line.journal_id.name, ))
                for line2 in line.analytics_id.account_ids:
                   val = (line.credit or  0.0) - (line.debit or 0.0)
                   amt= line2.rate and val * (line2.rate/100) or (line2.fix_amount)
                   al_vals={
                       'name': line.name,
                       'date': line.date,
                       'account_id': line2.analytic_account_id.id,
                       'unit_amount': line.quantity,
                       'product_id': line.product_id and line.product_id.id or False,
                       'product_uom_id': line.product_uom_id and line.product_uom_id.id or False,
                       'amount': amt,
                       'general_account_id': line.account_id.id,
                       'move_id': line.id,
                       'journal_id': line.analytics_id.journal_id and line.analytics_id.journal_id.id or line.journal_id.analytic_journal_id.id,
                       'ref': line.ref,
                       'department_id': line2.department_id.id,
                       'delegation_id': line2.delegation_id.id,
                       'manager_id': line2.manager_id.id,
                       'partner_id': line.move_id and line.move_id.partner_id and line.move_id.partner_id.id or False,
                   }
                   c = analytic_line_obj.create(cr, uid, al_vals, context=context)
        return True


account_move_line()
