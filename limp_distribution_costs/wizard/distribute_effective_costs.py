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
import time
import calendar
import tools

class distribution_effective_costs(osv.osv_memory):
    _name = "distribution.effective.costs"

    _columns = {
        'name': fields.char('Name',size=64,required=True),
        'month': fields.selection([
            ('1','January'), ('2','February'),
            ('3','March'), ('4','April'),
            ('5','May'), ('6','June'),
            ('7','July'), ('8','August'),
            ('9','September'), ('10','October'),
            ('11','November'), ('12','December')],'Month',required=True),
        'year': fields.integer('Year', required=True)
    }

    _defaults = {
        'year': lambda *a: int(time.strftime("%Y"))
    }

    def distribute_costs(self, cr, uid, ids, context = None):
        if context is None: context = {}
        obj = self.browse(cr, uid, ids[0])
        year = str(obj.year)
        month = str(obj.month).zfill(2)

        first_day, last_day = calendar.monthrange(int(year),int(month)) #obtenemos el último días del mes
        employees = self.pool.get('hr.employee').search(cr, uid, [])
        sueldos_journal_id = self.pool.get('account.analytic.journal').search(cr, uid, [('name', '=', 'Sueldos')])
        general_account_id_suelsala = self.pool.get('account.account').search(cr, uid, [('code','=',"64000000")])

        for employee in self.pool.get('hr.employee').browse(cr, uid, employees):
            #obtenemos los parte de horas del empleado dentro del mes importado
            timesheets = self.pool.get('timesheet').search(cr, uid, [('employee_id','=', employee.id),('date','>=',year+"-"+month+"-01"),('date','<=',year+"-"+month+"-"+str(last_day)),('done','=',True)])
            for timesheet in self.pool.get('timesheet').browse(cr, uid, timesheets):
                if timesheet.analytic_id:
                    ids_delete = self.pool.get('account.analytic.line').search(cr, uid,
                    [('timesheet_id','=',timesheet.id),('account_id','=',timesheet.analytic_id.id),
                    ('name','=',tools.ustr(obj.name)+u" (effective)/ "+month+u"/"+year+u"/ "+ employee.name)]) # borramos duplicados
                    if ids_delete:
                        self.pool.get('account.analytic.line').unlink(cr, uid, ids_delete)
                    amount = timesheet.effective
                    if amount:
                        vals = {
                            'amount': -(amount),
                            'name':  tools.ustr(obj.name)+u" (effective)/ "+month+u"/"+year+u"/ "+ employee.name,
                            'journal_id': sueldos_journal_id[0],
                            'timesheet_id': timesheet.id,
                            'account_id': timesheet.analytic_id.id,
                            'general_account_id': general_account_id_suelsala[0],
                            'date': year+"/"+month+"/"+str(calendar.monthrange(int(year),int(month))[1]),
                            'department_id': timesheet.department_id and timesheet.department_id.id or (timesheet.analytic_id.department_id and timesheet.analytic_id.department_id.id or False),
                            'delegation_id': timesheet.delegation_id and timesheet.delegation_id.id or (timesheet.analytic_id.delegation_id and timesheet.analytic_id.delegation_id.id or False),
                            'manager_id': timesheet.responsible_id and timesheet.responsible_id.id or (timesheet.analytic_id.manager_id and timesheet.analytic_id.manager_id.id or False),
                            'employee_id' : employee.id
                            }
                        self.pool.get('account.analytic.line').create(cr, uid, vals)

        return {'type': 'ir.actions.act_window_close'}


distribution_effective_costs()
