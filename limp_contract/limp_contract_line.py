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

"""Limpergal's contract lines, base object to support adding extension all Limpergal' sections"""

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp
import time

class limp_contract_line(osv.osv):
    """Limpergal's contract lines, base object to support adding extension all Limpergal' sections"""

    _name = "limp.contract.line"
    _description = "Limpergal's contract lines"
    _rec_name = 'num'

    def _get_incidences_amount(self, cr, uid, ids, field_name, arg, context=None):
        """Returns total amount of contract_line incidences"""
        if context is None: context = {}
        res = {}

        for line in self.browse(cr, uid, ids):
            amount = 0.0
            if line.incidence_ids:
                for incidence in line.incidence_ids:
                    amount += incidence.amount * incidence.hours

            res[line.id] = amount

        return res

    _columns = {
        'contract_id': fields.many2one('limp.contract', 'Contract', readonly=True, ondelete="cascade"),
        'num': fields.char('Num.', size=4, readonly="True"),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'), readonly=True),
        #'task_ids': fields.one2many('limp.contract.line.task.rel', 'contract_line_id', 'Tasks'),
        'employee_task_ids' : fields.one2many('limp.contract.line.employee.task','contract_line_id','Employees Tasks'),
        'incidence_ids': fields.one2many('limp.incidence', 'contract_line_id', 'Incidences'),
        'incidences_amount': fields.function(_get_incidences_amount, method=True, string="Incid. amount", readonly=True, type="float", digits_compute=dp.get_precision('Account')),
        'note': fields.text('Description'),
        'incidences': fields.boolean('Contents incidences'),
        'incidences_text': fields.text('Incidences description')
    }

limp_contract_line()
