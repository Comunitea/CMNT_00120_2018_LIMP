# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Pexego Sistemas Informáticos. All Rights Reserved
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

class account_analytic_target(osv.osv):
    _name = "account.analytic.target"
    _rec_name = "fiscalyear_id"
    _order = "fiscalyear_id desc"

    _columns = {
        'analytic_journal_id': fields.many2one('account.analytic.journal', 'Journal'),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'manager_id': fields.many2one('hr.employee', 'Responsible', domain=[('responsible', '=', True)]),
        'target_percent': fields.float('Percent target', digits=(5,2), required=True)
    }

    _defaults = {
        'company_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).company_id.id,
    }


account_analytic_target()
