# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos S.L.
#    $Omar Castiñeira Saavedra$ omar@comunitea.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields

class create_service_picking_from_sale(osv.osv_memory):

    _name = "create.service.picking.from.sale"

    _columns = {
        'picking_type': fields.selection([('wastes','Wastes'),('sporadic','Sporadic'),('maintenance', 'Maintenance')], 'Service picking type', required=True)
    }

    def action_create_picking(self, cr, uid, ids, context=None):
        if context is None: context = {}
        obj = self.browse(cr, uid, ids[0])
        context['picking_type'] = obj.picking_type
        res = self.pool.get('sale.order').create_pick(cr, uid, [context['active_id']], context=context)
        return res

create_service_picking_from_sale()
