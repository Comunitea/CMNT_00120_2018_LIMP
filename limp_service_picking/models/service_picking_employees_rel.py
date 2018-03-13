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
from odoo import models, fields
from odoo.addons import decimal_precision as dp

class ServicePickingEmployeesRel(models.Model):

    _name = "stock.service.picking.employees.rel"
    _description = "Relationship between services pickings and employees"

    picking_id = fields.Many2one('stock.service.picking', 'Picking', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    hours = fields.Float('Hours', digits=(4,2), required=True)
    total_amount = fields.Float('Amount total', digits=dp.get_precision('Account'), compute='_compute_total_amount')

    def _compute_total_amoun(self):
        for obj in self:
            if obj.employee_id.product_id:
                obj.total_amount = obj.employee_id.product_id.list_price * obj.hours
            else:
                obj.total_amount = 0.0
        return res
