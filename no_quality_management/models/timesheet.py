# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, api

class Timesheet(models.Model):

    _inherit = 'timesheet'

    scont = fields.Boolean('Scont', related='employee_id.scont', readonly=True)

    @api.model
    def create(self):
        scont = False
        if vals.get('employee_id', False):
            employee_obj = self.env['hr.employee'].browse(vals['employee_id'])
            if employee_obj.scont:
                vals['done'] = True
                scont = True

        res =  super(Timesheet, self).create(vals)
        if scont and res.pending_qty:
            res.write({'effective': res.pending_qty})
        return res

    def write(self, vals):
        scont = False
        if vals.get('employee_id', False):
            employee_obj = self.env['hr.employee'].browse(vals['employee_id'])
            if employee_obj.scont:
                vals['done'] = True
                scont = True
        else:
            if self.employee_id.scont:
                vals['done'] = True
                scont = True
        res = super(Timesheet, self).write(vals)
        if scont and self.pending_qty and not vals.get('effective', False):
            self.write({'effective': self.pending_qty})
        return res
