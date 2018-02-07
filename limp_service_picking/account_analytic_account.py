# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
from openerp.tools import drop_view_if_exists

class analytic_account_employees(osv.osv):

    _name = "analytic.account.employees"
    _auto = False

    _columns = {
        'analytic_id': fields.many2one("account.analytic.account", "Analytic", readonly=True),
        'employee_id': fields.many2one("hr.employee", "Employee", readonly=True),
        'hours': fields.float("Hours", readonly=True),
        'extra_hours': fields.float("Hours", readonly=True)
    }

    def init(self, cr):
        drop_view_if_exists(cr,  "analytic_account_employees")

        cr.execute("""
            create or replace view analytic_account_employees as (
            SELECT min(id) as id, employee_id, analytic_id,
            sum(hours) as hours, sum(extra_hours) as extra_hours
            FROM timesheet GROUP BY analytic_id, employee_id
            )""")

analytic_account_employees()


class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'

    def _get_distinct_employee_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for acc in self.browse(cr, uid, ids, context=context):
            employee_ids = []
            timesheet_ids = []

            for timesheet in acc.employee_ids:
                if timesheet.employee_id.id not in employee_ids:
                    employee_ids.append(timesheet.employee_id.id)
                    timesheet_ids.append(timesheet.id)
            res[acc.id] = timesheet_ids

        return res

    _columns = {
        'employee_ids': fields.one2many('timesheet', 'analytic_id', string='Timesheet'),
        'active_employee_ids': fields.one2many('timesheet', 'analytic_id', 'Active timesheets', domain=[('old','=',False)]),
        'inactive_employee_ids': fields.one2many('timesheet', 'analytic_id', 'Unactive timesheets', domain=[('old','=',True)]),
        'report_employee_ids': fields.one2many("analytic.account.employees", "analytic_id", string='Timesheet', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=False, change_default=True),
        'delegation_id': fields.many2one('res.delegation', 'Delegation', change_default=True),
        'other_expense_ids': fields.one2many('stock.service.other.expenses', 'analytic_id', string="Other expenses")
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'employee_ids': [],
            'line_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'other_expense_ids': [],
            'report_employee_ids': []
        })

        return super(account_analytic_account, self).copy(cr, 1, id, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'employee_ids': [],
            'line_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'other_expense_ids': [],
            'report_employee_ids': []
        })

        return super(account_analytic_account, self).copy_data(cr, uid, id, default, context)

account_analytic_account()
