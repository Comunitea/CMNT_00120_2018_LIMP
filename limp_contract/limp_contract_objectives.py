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

"""Master table of objectives by department"""

from openerp.osv import osv, fields

class limp_contract_objectives(osv.osv):
    """Master table of objectives by department"""

    _name = "limp.contract.objectives"
    _description = "Contract objectives"

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'department_id': fields.many2one('hr.department', 'Department', required=True),
    }

limp_contract_objectives()

class limp_contract_line(osv.osv):
    """Adds objectives relationship in contract"""

    _inherit = "limp.contract.line"

    _columns = {
        'objective_ids': fields.many2many('limp.contract.objectives', 'limp_contract_objectives_rel', 'contract_id', 'objective_id', 'Objectives')
    }

limp_contract_line()