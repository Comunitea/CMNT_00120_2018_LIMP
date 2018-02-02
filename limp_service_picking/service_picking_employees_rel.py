# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
import decimal_precision as dp

class service_picking_employees_rel(osv.osv):

    _name = "stock.service.picking.employees.rel"
    _description = "Relationship between services pickings and employees"

    def _get_hours_amount(self, cr, uid, ids, field_name, arg, context=None):
        """employee.hour_price * hours"""
        if context is None: context = {}
        res = {}

        for obj in self.browse(cr, uid, ids):
            if obj.employee_id.product_id:
                res[obj.id] = obj.employee_id.product_id.list_price * obj.hours
            else:
                res[obj.id] = 0.0
        return res

    _columns = {
        'picking_id': fields.many2one('stock.service.picking', 'Picking', required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'hours': fields.float('Hours', digits=(4,2), required=True),
        'total_amount': fields.function(_get_hours_amount, method=True, string="Amount total", readonly=True, type="float", digits_compute=dp.get_precision('Account'))
    }

service_picking_employees_rel()
