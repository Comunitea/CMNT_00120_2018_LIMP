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
from odoo import models, fields


class LimpContractLineTaskRel(models.Model):

    _name = "limp.contract.line.task.rel"
    _description = "Limpergal's contract lines and contract_tasks relationship"

    employee_task_line_id = fields.Many2one('limp.contract.line.employee.task','Employee Task')
    contract_task_id = fields.Many2one('limp.contract.task', 'Task', required=True)
    name = fields.Char('Name', related='contract_task_id.name')
    task_sequence = fields.Integer('Sequence', compute='_compute_task_sequence')
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('Saturday')
    sunday = fields.Boolean('Sunday')
    freq = fields.Selection(
        [('w', 'Weekly'),('m', 'Monthy'), ('q', 'Quarterly'),
         ('b', 'Biannual'), ('a', 'Annual'), ('ph', 'Per hours'),
         ('bm', 'Bimonthly'), ('2m', 'Two months'), ('d', 'Diary')],
        'Periodicity', default='w')
    observations = fields.Text('Observations')

    def _compute_sequence(self):
        for task in self:
            task.task_sequence = task.contract_task_id.sequence
