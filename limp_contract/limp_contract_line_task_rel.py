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

"""Relationship between contract line and contract task"""

from osv import osv, fields

class limp_contract_line_task_rel(osv.osv):
    """Relationship between contract line and contract task"""

    _name = "limp.contract.line.task.rel"
    _description = "Limpergal's contract lines and contract_tasks relationship"

    def _get_sequence(self, cr, uid, ids, name, args, context=None):
        res = {}
        for task in self.browse(cr, uid, ids):
            res[task.id] = task.contract_task_id.sequence

        return res

    _columns = {
        'employee_task_line_id': fields.many2one('limp.contract.line.employee.task','Employee Task'),
        'contract_task_id': fields.many2one('limp.contract.task', 'Task', required=True),
        'name': fields.related('contract_task_id', 'name', type="char", size=256, readonly=True, string="Name"),
        'task_sequence': fields.function(_get_sequence, method=True, type="integer", readonly=True, string="Sequence"),
        'monday': fields.boolean('Monday'),
        'tuesday': fields.boolean('Tuesday'),
        'wednesday': fields.boolean('Wednesday'),
        'thursday': fields.boolean('Thursday'),
        'friday': fields.boolean('Friday'),
        'saturday': fields.boolean('Saturday'),
        'sunday': fields.boolean('Sunday'),
        'freq': fields.selection([('w', 'Weekly'),('m', 'Monthy'), ('q', 'Quarterly'), ('b', 'Biannual'), ('a', 'Annual'), ('ph', 'Per hours'), ('bm', 'Bimonthly'), ('2m', 'Two months'), ('d', 'Diary')], 'Periodicity'),
        'observations': fields.text('Observations')
    }

    _defaults = {
        'freq': lambda *a: 'w',
    }

limp_contract_line_task_rel()
