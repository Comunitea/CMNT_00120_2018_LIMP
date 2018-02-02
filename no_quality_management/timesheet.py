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


from osv import osv, fields

class timesheet(osv.osv):

    _inherit = 'timesheet'

    _columns = {
        'scont': fields.related('employee_id', 'scont', string="Scont", type="boolean", readonly=True)
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        scont = False
        if vals.get('employee_id', False):
            employee_obj = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'])
            if employee_obj.scont:
                vals['done'] = True
                scont = True

        res =  super(timesheet, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, res)
        if scont and obj.pending_qty:
            self.write(cr, uid, [res], {'effective': obj.pending_qty})

        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: contex = {}
        scont = False
        if vals.get('employee_id', False):
            employee_obj = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'])
            if employee_obj.scont:
                vals['done'] = True
                scont = True
        else:
            obj = self.browse(cr, uid, ids[0])
            if obj.employee_id.scont:
                vals['done'] = True
                scont = True

        res = super(timesheet, self).write(cr, uid, ids, vals, context=context)
        obj = self.browse(cr, uid, ids[0])
        if scont and obj.pending_qty and not vals.get('effective', False):
            self.write(cr, uid, [ids[0]], {'effective': obj.pending_qty})

        return res

timesheet()
