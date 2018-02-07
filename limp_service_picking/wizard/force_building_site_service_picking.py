# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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

from openerp.osv import osv, fields

class force_building_site_service_picking(osv.osv_memory):
    
    _name = "force.building.site.service.picking"
    
    _columns = {
        'service_picking_id': fields.many2one('stock.service.picking', 'Picking', required=True)
    }    
    
    def copy_building_site(self, cr, uid, ids, context=None):
        if context is None: context = {}
        
        obj = self.browse(cr, uid, ids[0])
        self.pool.get('stock.service.picking').write(cr, uid, context['active_ids'], {'building_site_id': obj.service_picking_id.building_site_id.id})
        
        return {}
    
force_building_site_service_picking()
