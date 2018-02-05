# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos
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

from openerp import models, fields
from tools.translate import _
import time


class employee_incidence_set_end_date_wzd(models.TransientModel):

    _name = "employee.incidence.set.end.date.wzd"

    _columns = {
        'date': fields.date('Date',required=True),
        'only_incidences': fields.boolean('Only incidences', help="Sets end date in incidences only, if not check it sets the end date in all open remunerations.")
    }

    _defaults = {
        'only_incidences': True,
        'date': lambda *a: time.strftime("%Y-%m-%d")
    }

    def act_set_end_date(self, cr, uid, ids, context=None):
        if context is None: context = {}
        employee_id = context.get('active_id', False)
        obj = self.browse(cr, uid, ids[0])
        domain = [('employee_id', '=', employee_id),('date_to','=',False)]

        if obj.only_incidences:
            action_model, type_incidence_normal_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'analytic_incidences', 'incidence_normal')
            domain.append(('incidence_id_tp', '!=', type_incidence_normal_id))
        remunerations_ids = self.pool.get('remuneration').search(cr, uid, domain)
        if remunerations_ids:
            self.pool.get('remuneration').write(cr, uid, remunerations_ids, {'date_to': obj.date})
        open_incidences_ids = self.pool.get('hr.laboral.incidence').search(cr, uid, [('employee_id', '=', employee_id),('end_date', '=', False)])
        if open_incidences_ids:
            self.pool.get('hr.laboral.incidence').write(cr, uid, open_incidences_ids, {'end_date': obj.date})

        return {
        'type': 'ir.actions.act_window_close',
        }

employee_incidence_set_end_date_wzd()
