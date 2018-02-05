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

"""Master table of contract task by section or department"""

from openerp import models, fields
from tools.translate import _

class limp_contract_task(models.Model):
    """Master table of contract task by section or department"""

    _name = "limp.contract.task"
    _description = "Limpergal contract tasks"

    _order = "sequence asc"

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'department_id': fields.many2one('hr.department', 'Department', required=True),
        'parent_id': fields.many2one('limp.contract.task', 'Parent Task'),
        'sequence': fields.integer('Sequence'),
        'company_id': fields.many2one('res.company', 'Company'),
        'center_type_id': fields.many2one("limp.center.type", "Center type")
    }

    _defaults = {
        'sequence': lambda *a: 0
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        """avoid recursion in contract tasks"""
        if context is None:
            context = {}

        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from limp_contract_task where id IN %s', (tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, _('Error! You can not create recursive tasks.'), ['parent_id'])
    ]

limp_contract_task()
