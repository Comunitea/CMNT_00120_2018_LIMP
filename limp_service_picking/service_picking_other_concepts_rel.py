# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
from openerp import models, fields
import decimal_precision as dp
from tools.translate import _

class service_picking_other_concepts_rel(models.Model):
    _name = 'service.picking.other.concepts.rel'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'name': fields.char('Name', size=256, required=True),
        'product_qty': fields.float('Qty.', digits=(12,3), required=True),
        'service_picking_id': fields.many2one('stock.service.picking', 'Service picking'),
        'billable' : fields.boolean('Billable')
    }

    _defaults = {
        'billable': True,
        'product_qty': 1
    }

    def onchange_product_id_warning(self,cr,uid,ids,product_id):
        res = {}
        if not product_id:
            return res
        product_obj = self.pool.get('product.product').browse(cr, uid, product_id)

        res['value'] = {'name': product_obj.name}

        warning = {}
        if product_obj.picking_warn != 'no-message':
            if product_obj.picking_warn == 'block':
                raise osv.except_osv(_('Alert for %s !') % (product_obj.name), product_obj.picking_warn_msg)
            title = _("Warning for %s") % product_obj.name
            message = product_obj.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
            res['warning'] = warning

        return res


service_picking_other_concepts_rel()
