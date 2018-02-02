# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class stock_service_other_expenses(osv.osv):

    _name = "stock.service.other.expenses"

    def _get_subtotal(self,cr,uid,ids,field_name,args,context=None):
        res = {}
        for expense in self.browse(cr, uid, ids):
            res[expense.id] = expense.price_unit * expense.prod_qty
        return res

    _columns = {
        'name': fields.char('Description', required=True, size=255),
        'prod_qty': fields.float('Qty.', digits=(16,2), required=True),
        'price_unit': fields.float('Price unit', required=True),
        'price_subtotal': fields.function(_get_subtotal, method=True, string="Subtotal", type="float", digits=(16,2), readonly=True,
            store = {
                'stock.service.other.expenses': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'prod_qty'], 10)}),
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic')
    }

stock_service_other_expenses()
