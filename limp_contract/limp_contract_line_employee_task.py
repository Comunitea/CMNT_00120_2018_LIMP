# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

"""Relationship between contract line and employees and tasks"""

from openerp.osv import osv, fields
from openerp.tools.translate import _

class limp_contract_line_employee_task(osv.osv):
    """Relationship between contract line and employees and tasks"""

    _name = "limp.contract.line.employee.task"
    _description = "Contract employees tasks relationship"
    _rec_name = "timetable"

    def _get_employees_str(self, cr, uid, ids, name, args, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = u" / ".join([x.name for x in task.employee_ids])

        return res

    _columns = {
        'id' : fields.integer('id',readonly=True),
        'contract_line_id': fields.many2one('limp.contract.line', 'Contract line'),
        'contract_id': fields.related('contract_line_id', 'contract_id', type="many2one", relation="limp.contract", readonly=True, string="Contract"),
        'department_id': fields.related('contract_id', 'department_id', type="many2one", relation="hr.department", readonly=True, string="Department"),
        #'employee_id': fields.many2one('hr.employee', 'Employees', required=True),
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_contract_task_rel', 'contract_task_id', 'employee_id', 'Employees'),
        'employee_str': fields.function(_get_employees_str, method=True, type="text", readonly=True, string="Employees"),
        'end_date': fields.date('End date'),
        'task_ids': fields.one2many('limp.contract.line.task.rel', 'employee_task_line_id', 'Tasks'),
        'timetable': fields.text('Timetable'),
        'project_date': fields.date('Project date'),

    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        res = super(limp_contract_line_employee_task, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, res)
        if obj.contract_id.sale_id and obj.contract_id.sale_id.task_frequency_ids:
            self.get_order_tasks(cr, uid, [res])
        else:
            self.get_all_tasks(cr, uid, [res])

        return res

    def get_order_tasks(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if line.contract_id.sale_id:
                task_ids = self.pool.get('limp.contract.line.task.rel').search(cr, uid, [('employee_task_line_id', '=', line.id)])
                self.pool.get('limp.contract.line.task.rel').unlink(cr, uid, task_ids)
                vals = {}
                for freq_task in line.contract_id.sale_id.task_frequency_ids:
                    if freq_task.task_id:
                        if freq_task.lu or freq_task.ma or freq_task.mi or freq_task.ju or freq_task.vi or freq_task.sa or freq_task.do:
                            monday = freq_task.lu or False
                            tuesday = freq_task.ma or False
                            wednesday = freq_task.mi or False
                            thursday = freq_task.ju or False
                            friday = freq_task.vi or False
                            saturday = freq_task.sa or False
                            sunday = freq_task.do or False
                        if freq_task.sm: #semanal
                            freq = "w"
                        elif freq_task.qc: #quincenal
                            freq = "bm"
                        elif freq_task.m: #mensual
                            freq = "m"
                        elif freq_task.bt: #bimensual
                            freq = "2m"
                        elif freq_task.tr: #trimestral
                            freq = "q"
                        elif freq_task.st: #semestral
                            freq = "b"
                        elif freq_task.an: #anual
                            freq = "a"
                        else:
                            freq = False
                        vals = {
                            'monday': monday,
                            'tuesday': tuesday,
                            'wednesday': wednesday,
                            'thursday': thursday,
                            'friday': friday,
                            'saturday': saturday,
                            'sunday': sunday,
                            'freq': freq,
                            'contract_task_id': freq_task.task_id.id,
                            'employee_task_line_id': line.id,
                            'observations': freq_task.description
                        }
                        self.pool.get('limp.contract.line.task.rel').create(cr, uid, vals)
        return True

    def get_all_tasks(self, cr, uid, ids, context=None):
        """Load all task related with this contract line"""
        if context is None: context = {}

        for line in self.browse(cr, uid, ids):
            if not line.department_id:
                raise osv.except_osv(_('Error!'), _('Not department defined for this contract line'))
            task_ids = self.pool.get('limp.contract.task').search(cr, uid, ['|', ('department_id', '=', line.department_id.id), ('department_id', '=', False)])

            for task in task_ids:
                task_rels = self.pool.get('limp.contract.line.task.rel').search(cr, uid, [('employee_task_line_id', '=', line.id), ('contract_task_id', '=', task)])
                if not task_rels:
                    self.pool.get('limp.contract.line.task.rel').create(cr, uid, {'employee_task_line_id': line.id,'contract_task_id': task})
        return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        if not context:
            context = {}
        if context.get('is_contract', False):
            task = self.browse(cr, uid, id)
            if task.end_date:
                return {}
        default.update({'end_date': False})
        return super(limp_contract_line_employee_task, self).copy_data(cr, uid, id, default, context)


limp_contract_line_employee_task()
