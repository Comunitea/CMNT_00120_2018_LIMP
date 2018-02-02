# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiéira Saavedra$
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

"""Adds fields to employee object"""

from osv import osv, fields
from datetime import datetime

class hr_employee(osv.osv):
    """Adds fields to employee object"""

    _inherit = "hr.employee"

    def _get_active_remunerations(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        current_date = datetime.now().strftime("%Y-%m-%d")
        for employee_id in ids:
            remuneration_ids = self.pool.get('remuneration').search(cr, uid, [('employee_id', '=', employee_id),'|',('date_to', '=', False),('date_to', '>=', current_date)])
            if remuneration_ids:
                res[employee_id] = True
            else:
                res[employee_id] = False
        return res

    _columns = {
        'laboral_incidence_ids': fields.one2many('hr.laboral.incidence', 'employee_id', 'Incidences', readonly=True),
        'work_council_id': fields.many2one('city.council', 'Work council'),
        'active_remunerations': fields.function(_get_active_remunerations, method=True, type="boolean", string="Active remunerations", readonly=True)
    }

hr_employee()
