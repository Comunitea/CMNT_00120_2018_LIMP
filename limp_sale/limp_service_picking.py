# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from openerp.addons.decimal_precision import decimal_precision as dp

class limp_service_picking(osv.osv):
    _inherit = 'stock.service.picking'

    _columns = {
        'sale_id': fields.many2one("sale.order", string="Sale"),
        'sale_line_ids': fields.related('sale_id', 'order_line', type="one2many", relation="sale.order.line", string="Order lines", readonly=True)
    }

    _defaults = {
        'pricelist_id': lambda self, cr, uid, context: context.get('pricelist', False),
    }

limp_service_picking()

class service_picking_invoice_concept(osv.osv):

    _inherit = "service.picking.invoice.concept"

    def product_id_change(self, cr, uid, ids, product_id, product_qty=0.0, product_uom=False, name='', address_id=False, fpos=False, pricelist=False, date=False, context=None):
        if context is None: context = {}
        product_obj = self.pool.get('product.product')
        res = super(service_picking_invoice_concept, self).product_id_change(cr, uid, ids, product_id, product_qty=product_qty, product_uom=product_uom, name=name, address_id=address_id, fpos=fpos, context=context)
        if date:
            context['date'] = date

        price = 0
        if product_id:
            product_obj = product_obj.browse(cr, uid, product_id, context=context)
            if address_id:
                factor = 0
                if product_obj.price_rule_ids:
                    assigned= False
                    for price_rule_id in product_obj.price_rule_ids:
                        if product_qty and address_id:
                            address_obj = self.pool.get('res.partner.address').browse(cr, uid, address_id)
                            if address_obj.state_id:
                                if price_rule_id.province and price_rule_id.province.id == address_obj.state_id.id:
                                    if product_qty >= price_rule_id.range:
                                        factor = price_rule_id.price
                                        assigned = True
                            else:
                                if not price_rule_id.province:
                                    if product_qty >= price_rule_id.range:
                                        factor = price_rule_id.price
                                        assigned = True
                    if not assigned:
                        for price_rule_id in product_obj.price_rule_ids:
                            if not price_rule_id.province and product_qty >= price_rule_id.range:
                                factor = price_rule_id.price

                    if factor:
                        price = factor

            if price and pricelist:
                pricelist_price = self.pool.get('product.pricelist').apply_pricelist_to_price(cr, uid, [pricelist], res['value']['price'], product_id, res['value']['product_qty'], context=context)
                if pricelist_price:
                    res['value']['price'] = pricelist_price
                    res['value']['subtotal'] = product_qty * pricelist_price
            elif pricelist:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product_id, product_qty or 1.0, context=context)[pricelist]
                if price:
                    res['value']['price'] = price
                    res['value']['subtotal'] = product_qty * price
            else:
                res['value']['price'] = product_obj.list_price
                res['value']['subtotal'] = product_qty * product_obj.list_price

        return res



service_picking_invoice_concept()

class service_picking_other_concepts_rel(osv.osv):
    _inherit = 'service.picking.other.concepts.rel'

    _columns = {
        'price_unit': fields.float('Price Unit', digits_compute = dp.get_precision('Sale Price'))
    }

    def onchange_product_id_warning(self,cr,uid,ids, product_id, sale_line_ids = [], address_id=False, pricelist=False, date=False, context=None):
        if context is None: context = {}
        if not product_id:
            return {}

        res = super(service_picking_other_concepts_rel, self).onchange_product_id_warning(cr, uid, ids, product_id)
        price_unit = 0.0
        description = False
        if sale_line_ids:
            if isinstance(sale_line_ids, list) and isinstance(sale_line_ids[0], tuple):
                sale_line_ids  = [x[1] for x in sale_line_ids]
            line_ids = self.pool.get('sale.order.line').search(cr, uid, [('id', 'in', sale_line_ids),('product_id','=',product_id)])
            if line_ids:
                sale_line_obj = self.pool.get('sale.order.line').browse(cr, uid, line_ids[0])
                price_unit = sale_line_obj.price_unit
                description = sale_line_obj.name

        if date:
            context['date'] = date

        if address_id and not price_unit:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
            factor = 0
            price = 0.0
            if product_obj.price_rule_ids:
                assigned= False
                for price_rule_id in product_obj.price_rule_ids:
                    if product_qty and address_id:
                        address_obj = self.pool.get('res.partner.address').browse(cr, uid, address_id)
                        if address_obj.state_id:
                            if price_rule_id.province and price_rule_id.province.id == address_obj.state_id.id:
                                if product_qty >= price_rule_id.range:
                                    factor = price_rule_id.price
                                    assigned = True
                        else:
                            if not price_rule_id.province:
                                if product_qty >= price_rule_id.range:
                                    factor = price_rule_id.price
                                    assigned = True
                if not assigned:
                    for price_rule_id in product_obj.price_rule_ids:
                        if not price_rule_id.province and product_qty >= price_rule_id.range:
                            factor = price_rule_id.price

                if factor:
                    price = factor

            if price and pricelist:
                pricelist_price = self.pool.get('product.pricelist').apply_pricelist_to_price(cr, uid, [pricelist], res['value']['price_unit'], product_id, 1, context=context)
                if pricelist_price:
                    price_unit = pricelist_price
            elif pricelist:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product_id, 1.0, context=context)[pricelist]
                if price:
                    price_unit = price
            else:
                price_unit = product_obj.list_price

        if price_unit:
            res['value']['price_unit'] = price_unit
        if description:
            res['value']['name'] = description

        return res


service_picking_other_concepts_rel()
