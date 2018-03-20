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
from odoo import models, fields, _
from odoo.exceptions import UserError

class LimpContractLineEmployeeTask(models.Model):
    """Relationship between contract line and employees and tasks"""

    _name = "limp.contract.line.employee.task"
    _description = "Contract employees tasks relationship"
    _rec_name = "timetable"

    id = fields.Integer('id',readonly=True)
    contract_line_id = fields.Many2one('limp.contract.line', 'Contract line')
    contract_id = fields.Many2one('limp.contract', string='Contract', related='contract_line_id.contract_id', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', related='contract_id.department_id', readonly=True)
    #'employee_id': fields.many2one('hr.employee', 'Employees', required=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_contract_task_rel', 'contract_task_id', 'employee_id', 'Employees')
    employee_str = fields.Text("Employees", compute='_compute_employees_str')
    end_date = fields.Date('End date')
    task_ids = fields.One2many('limp.contract.line.task.rel', 'employee_task_line_id', 'Tasks')
    timetable = fields.Text('Timetable')
    project_date = fields.Date('Project date')

    def _compute_employees_str(self):
        for task in self:
            task.employee_str = u" / ".join([x.name for x in task.employee_ids])

    def create(self, vals):
        res = super(LimpContractLineEmployeeTask, self).create(vals)
        if res.contract_id.sale_id and res.contract_id.sale_id.task_frequency_ids:
            res.get_order_tasks()
        else:
            res.get_all_tasks()

        return res

    def get_order_tasks(self):
        for line in self:
            if line.contract_id.sale_id:
                task_ids = self.env['limp.contract.line.task.rel'].search([('employee_task_line_id', '=', line.id)])
                task_ids.unlink()
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
                        self.env['limp.contract.line.task.rel'].create(vals)
        return True

    def get_all_tasks(self):
        for line in self:
            if not line.department_id:
                raise UserError(_('Not department defined for this contract line'))
            task_ids = self.env['limp.contract.task'].search(['|', ('department_id', '=', line.department_id.id), ('department_id', '=', False)])

            for task in task_ids:
                task_rels = self.env['limp.contract.line.task.rel'].search([('employee_task_line_id', '=', line.id), ('contract_task_id', '=', task.id)])
                if not task_rels:
                    self.env['limp.contract.line.task.rel'].create({'employee_task_line_id': line.id, 'contract_task_id': task.id})
        return True

    def copy_data(self, default=None):
        if self._context.get('is_contract', False):
            if self.end_date:
                return {}
        default.update({'end_date': False})
        return super(LimpContractLineEmployeeTask, self).copy_data(default)
