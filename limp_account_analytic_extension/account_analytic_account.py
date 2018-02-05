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

class account_analytic_account(osv.osv):

    _inherit = "account.analytic.account"

    _order = "name desc"

    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation', change_default=1),
        'custom_manager_id': fields.many2one('hr.employee', 'Responsible', domain=[('responsible', '=', True)]), # MIGRACION: Se cambia el nombre de la columna, ya que el modulo project añade otra con el mismo nombre
    }

    _defaults = {
        'delegation_id': lambda self, cr, uid, context: context.get('delegation_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context).context_delegation_id.id,
        # 'department_id': lambda s,cr,uid,c: c.get('department_id', False) or s.pool.get('res.users').browse(cr,uid,uid).context_department_id.id,  MIGRACION: El campo context_department_id no existe
        'custom_manager_id': lambda self, cr, uid, context: context.get('c_manager_id',False) or self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context) and self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)[0] or False,
    }

account_analytic_account()

class account_analytic_line(osv.osv):
    """Adds new fields to analytics accounts"""

    _inherit = "account.analytic.line"

    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'manager_id': fields.many2one('hr.employee', 'Responsible', domain=[('responsible', '=', True)]),
        'move_id': fields.many2one('account.move.line', 'Move Line', ondelete='cascade', select=True),
        "employee_id": fields.many2one('hr.employee','Employee'),
        "partner_id": fields.many2one('res.partner','Partner'),
    }

    _defaults = {
        'delegation_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).context_delegation_id.id,
        'manager_id': lambda self, cr, uid, context: context.get('c_manager_id',False) or self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context) and self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)[0] or False,
    }

account_analytic_line()
