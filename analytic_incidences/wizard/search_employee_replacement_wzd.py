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
from datetime import datetime
from openerp.tools.translate import _

class search_employee_replacemenet(osv.osv_memory):

    _name = "search.employee.replacement"
    _description = "Search for possible replacement"

    def _get_default_department(self, cr, uid, context=None):
        """returns employee department od occupation department"""
        if context is None: context = {}

        if context.get('department', False):
            return context['department']
        elif context.get('employee_id', False):
            employee = self.pool.get('hr.employee').browse(cr, uid, context['employee_id'])
            if employee.department_ids:
                return employee.department_ids[0].id

        return False

    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employees_search_replacement_rel', 'replacement_id', 'employee_id', string="Possible replacements"),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True, help="Employee to replace"),
        'start_date': fields.date('Start date', required=True),
        'end_date': fields.date('End date', required=True),
        'location': fields.many2one('city.council', 'Council'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'hour_no': fields.float('Number of hours', digits=(12, 2), required=True, help="Number of hours between dates take in account 8 per day")
    }

    _defaults = {
        'start_date': lambda s,c,u,ctx: ctx.get('start_date', False),
        'end_date': lambda s,c,u,ctx: ctx.get('end_date', False),
        'department_id': _get_default_department,
        'location': lambda s,c,u,ctx: ctx.get('location', False),
        'employee_id': lambda s,c,u,ctx: ctx.get('employee_id', False),
        'hour_no': 0.0
    }

    def search_replacements(self, cr, uid, ids, context=None):
        """search for replacements"""
        if context is None: context = {}

        obj = self.browse(cr, uid, ids[0])
        employee_domain = []
        possible_employees = []
        if obj.location:
            employee_domain.append(('work_council_id', '=', obj.location.id))
#        if obj.department_id:
#            employee_domain.append(('department_ids', 'in', [obj.department_id.id]))
        if obj.employee_id:
            employee_domain.append(('id', '!=', obj.employee_id.id))
        employees = self.pool.get('hr.employee').search(cr, uid, employee_domain)

        for x in self.pool.get('hr.employee').browse(cr, uid, employees):
            if x.department_ids:
                for y in x.department_ids:
                    if y.id == obj.department_id.id:
                        possible_employees.append(x.id)


        real_possible_employees = []
        if possible_employees:
            for employee in self.pool.get('hr.employee').browse(cr, uid, possible_employees):
                total_availability = datetime.strptime(obj.end_date, "%Y-%m-%d") - datetime.strptime(obj.start_date, "%Y-%m-%d")
                total_availability = total_availability.days * 8
                if total_availability < 0:
                    raise osv.except_osv(_('Error!'),_("Incorrect range of dates"))
                occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('employee_id', '=', employee.id), ('state', 'in', ['active','replacement']), ('date', '>=', obj.start_date), ('date', '<=', obj.end_date)])
                total_occupation = 0.0
                for occupation in self.pool.get('account.analytic.occupation').browse(cr, uid, occupation_ids):
                    total_occupation += occupation.duration

                if total_availability >= total_occupation + obj.hour_no:
                    real_possible_employees.append(employee.id)

        obj.write({'employee_ids': [(6, 0, real_possible_employees)]})

        return True

search_employee_replacemenet()
