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
from osv import osv, fields
import decimal_precision as dp

class price_rule(osv.osv):
    
    _name = 'price.rule'
    _description = 'Price rules'
    
    _columns = {
        'name': fields.char('Name', size=255, readonly=True, required=True),
        'range': fields.integer('Range', required=True),
        'province': fields.many2one('res.country.state', 'Province'),
        'product_id': fields.many2one('product.product', 'Product'),
        'price': fields.float('Price', digits_compute=dp.get_precision('Account')),
        'cost_price': fields.float('Cost Price', digits_compute=dp.get_precision('Account'))
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'price.rule'),
    }
    
    _order = 'range asc'
    
price_rule()
