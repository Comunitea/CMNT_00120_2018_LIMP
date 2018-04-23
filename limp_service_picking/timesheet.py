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
        'building_site_id': fields.many2one('building.site.services', 'Building site/Service'),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        if vals.get('analytic_id', False):
            picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [('analytic_acc_id', '=', vals['analytic_id'])])
            if picking_ids:
                pick_id = self.pool.get('stock.service.picking').browse(cr, uid, picking_ids[0])
                if pick_id.building_site_id:
                    vals['building_site_id'] = pick_id.building_site_id.id

        return super(timesheet, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: contex = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        #changed = False
        if not vals:
            return True

        for tobj in self.browse(cr, uid, ids):
            picking_ids = self.pool.get('stock.service.picking').search(cr, uid, [('analytic_acc_id', '=', vals.get('analytic_id', tobj.analytic_id.id))])
            if picking_ids:
                pick_id = self.pool.get('stock.service.picking').browse(cr, uid, picking_ids[0])
                if pick_id.building_site_id:
                    vals['building_site_id'] = pick_id.building_site_id.id
                else:
                    vals['building_site_id'] = False
            #if picking_ids and (vals.get('extra_hours', False) or vals.get('quantity', False) or vals.get('price_hours', False)) and vals.get('done', False) != True:
            #    vals['done'] = False
            #    vals['contract'] = False
            #elif picking_ids and vals.get('done', False) != True:
            #    vals['done'] = True
            #    vals['contract'] = True
            #    changed = True
            super(timesheet, self).write(cr, uid, [tobj.id], vals, context=context)
            #if changed:
            #    changed = False
            #    vals['done'] = False
            #    vals['contract'] = False

        return True

timesheet()
