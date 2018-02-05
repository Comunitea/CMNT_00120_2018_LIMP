# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$ omar@pexego.es
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

from openerp import models, fields
from tools.translate import _


class print_product_pricelist(models.TransientModel):
    _name = 'print.product.pricelist'
    _description = 'Print product pricelist'

    _columns = {
        'state_id': fields.many2one('res.country.state', 'State', help="Filter prices by state.", required=True),
        'price_list': fields.many2one('product.pricelist', 'PriceList'),
        'qty1': fields.integer('Quantity-1'),
        'qty2': fields.integer('Quantity-2'),
        'qty3': fields.integer('Quantity-3'),
        'qty4': fields.integer('Quantity-4'),
        'qty5': fields.integer('Quantity-5'),
    }
    _defaults = {
        'qty1': 1,
        'qty2': 5,
        'qty3': 10,
        'qty4': 500,
        'qty5': 100,
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['state_id','qty1', 'qty2','qty3','qty4','qty5','price_list'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'product.pricelist.onprice.rule',
            'datas': datas,
       }
print_product_pricelist()
