# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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

class service_picking_invoice_concept(models.Model):

    _order = "sequence asc"

    def _get_subtotal(self,cr,uid,ids,field_name,args,context={}):
        res = {}
        for obj in self.browse(cr,uid,ids):
            res[obj.id] = obj.product_qty * obj.price
        return res

    def _get_taxes_str(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for obj in self.browse(cr,uid,ids):
            if obj.tax_ids:
                res[obj.id] = u", ".join([x.name for x in obj.tax_ids])
            else:
                res[obj.id] = ""
        return res

    _name = 'service.picking.invoice.concept'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'name': fields.char('Name', size=256, required=True),
        'price': fields.float('Price', digits=(12,2)),
        'notes': fields.text('Notes'),
        'product_qty': fields.float('Qty.', digits=(12,3)),
        'product_uom': fields.many2one('product.uom', 'Product uom'),
        'service_picking_id': fields.many2one('stock.service.picking', 'Service picking'),
        'subtotal': fields.function(_get_subtotal, method=True, type="float", string='Subtotal', readonly=True),
        'tax_ids': fields.many2many('account.tax', 'invoice_concept_tax_rel', 'concept_line_ids', 'tax_ids', 'Taxes'),
        'taxes_str': fields.function(_get_taxes_str, method=True, string="Taxes", type="text", readonly=True),
        'sequence': fields.integer('Seq.')
    }

    _defaults = {
        'sequence': 1
    }

    def on_change_price(self,cr,uid,ids,product_qty,price):
        res = {'value':{}}
        res['value']['subtotal'] = product_qty * price
        return res

    def product_id_change(self, cr, uid, ids, product_id, product_qty=0.0,product_uom=False, name='', address_id=False, fpos=False, context=None):
        result = {}
        warning = {}
        product_obj = self.pool.get('product.product')
        if product_id:
            product_obj = product_obj.browse(cr, uid, product_id)
            result['product_qty'] = product_qty
            result['notes'] = product_obj.description
            result['product_uom'] = product_obj.uom_id.id
            fpos = fpos and self.pool.get('account.fiscal.position').browse(cr, uid, fpos) or False
            result['tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
            result['price'] = product_obj.list_price
            result['subtotal'] = product_qty * result['price']

            if product_obj.picking_warn != 'no-message':
                if product_obj.picking_warn == 'block':
                    raise osv.except_osv(_('Alert for %s !') % (product_obj.name), product_obj.picking_warn_msg)
                title = _("Warning for %s") % product_obj.name
                message = product_obj.picking_warn_msg
                warning['title'] = title
                warning['message'] = message
        return {'value': result, 'warning':warning}



service_picking_invoice_concept()
