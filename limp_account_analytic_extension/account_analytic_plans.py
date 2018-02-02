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

class account_analytic_plan_instance_line(osv.osv):

    _inherit = "account.analytic.plan.instance.line"

    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation', required=True),
        'department_id': fields.many2one('hr.department', 'Department', required=True),
        'manager_id': fields.many2one('hr.employee', 'Responsible', required=True, domain=[('responsible', '=', True)]),
        'fix_amount': fields.float('Fix amount', digits=(12,2), required=True)
    }

    _defaults = {
        'delegation_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).context_delegation_id.id,
        'department_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).context_department_id.id,
        'manager_id': lambda self, cr, uid, context: self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0] or False,
    }

account_analytic_plan_instance_line()

class account_analytic_plan_instance(osv.osv):

    _inherit = "account.analytic.plan.instance"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company')
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    }

account_analytic_plan_instance()
