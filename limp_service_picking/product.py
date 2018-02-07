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

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp

class product_template(osv.osv):

    _inherit = "product.template"

    _columns = {
        'ler_code_id': fields.many2one('waste.ler.code', 'LER'),
        'overload_price': fields.float('Overload price', digits_compute=dp.get_precision('Sale Price'))
    }
    


product_template()
class product_product(osv.osv):
    _inherit = 'product.product'
    
    def get_price_product(self, cr, uid, ids, address_id=False, measure=False, pricelist=False, context=None):
        if context is None: context = {}
        vals = {}
        price = False
        product_obj = self.browse(cr, uid, ids)[0]
        if address_id and measure:
            factor = 0
            address_obj = self.pool.get('res.partner.address').browse(cr, uid, address_id)
            if product_obj.price_rule_ids:
                assigned= False
                for price_rule_id in product_obj.price_rule_ids:
                    if address_obj.state_id:
                        if price_rule_id.province and price_rule_id.province.id == address_obj.state_id.id:
                            if measure >= price_rule_id.range:
                                factor = price_rule_id.price
                                assigned = True
                        else:
                            if not price_rule_id.province:
                                if measure >= price_rule_id.range:
                                    factor = price_rule_id.price
                                    assigned = True
                if not assigned:
                    for price_rule_id in product_obj.price_rule_ids:
                        if not price_rule_id.province and measure >= price_rule_id.range:
                            factor = price_rule_id.price

                if factor:
                    price = factor

        if not price:
            price = product_obj.list_price
            
        if pricelist:
            pricelist_price = self.pool.get('product.pricelist').apply_pricelist_to_price(cr, uid, [pricelist], price, product_obj.id, measure, context=context)
            if pricelist_price:
                price = pricelist_price
            
        return price
        
product_product()
