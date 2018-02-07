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
import time

class fleet_expense(osv.osv):
    """Model to registry fleet expenses"""

    _name = "fleet.expense"
    _description = "Fleet expenses"
    _order = "km desc, expense_date desc"

    def _get_net_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        for expense in self.browse(cr, uid, ids):
            if expense.expense_type:
                if expense.expense_type.product_id:
                    rec = self.pool.get('account.tax').compute_inv(cr, uid, expense.expense_type.product_id.supplier_taxes_id, expense.amount, 1, product=expense.expense_type.product_id or False, partner=expense.partner_id or False)
                    res[expense.id] = 0.0
                    for e in rec:
                        res[expense.id] += e['price_unit']
            if not res.get(expense.id):
                res[expense.id] = expense.amount

        return res

    def _get_consumption(self, cr, uid, ids, name, args, context=None):
        res = {}
        action_model,type_expense_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'simple_fleet_management', 'fleet_expense_type_refueling')
        for expense in self.browse(cr, uid, ids):
            if expense.expense_type  and expense.expense_type.id == type_expense_id:
                expense_ids = self.search(cr, uid, [('km','<',expense.km),('expense_type','=',type_expense_id),('fleet_id','=',expense.fleet_id.id)], limit=1)
                if expense_ids:
                    expense_old = self.browse(cr, uid, expense_ids[0])
                    if expense_old.km and expense.km:
                        res[expense.id] = (expense.liter / (expense.km - expense_old.km)) * 100.0
                    else:
                        res[expense.id] = 0.0
                else:
                    res[expense.id] = 0.0
            else:
                res[expense.id] = 0.0

        return res

    _columns = {
        'expense_date': fields.date('Date', required=True),
        'name': fields.char('Description', size=256, required=True),
        'fleet_id': fields.many2one('fleet', 'Vehicle', required=True),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'), required=True),
        'net_amount': fields.function(_get_net_amount, method=True, string='Net amount', type="float", digits_compute=dp.get_precision('Account'), readonly=True),
        'note': fields.text('Note'),
        'expense_type': fields.many2one('fleet.expense.type', 'Type', help="Expense type"),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        'labor':fields.float('Labor',digits_compute=dp.get_precision('Account')),
        'parts_price':fields.float('Parts price',digits_compute=dp.get_precision('Account')),
        'liter':fields.float('Liter',digits_compute=dp.get_precision('Account')),
        'km':fields.float('Km',digits_compute=dp.get_precision('Account')),
        'distribute': fields.boolean('Distribute'),
        'department_id': fields.many2one("hr.department", "Department", required=True),
        'consumption': fields.function(_get_consumption, method=True, type="float", string="Consumption (l/100Km)", readonly=True, digits=(13,2), help="Liters each 100 km. (Refuel liters / traveled km) * 100")
    }

    _defaults = {
        'amount': 0.0,
        'distribute': True,
        'expense_date': lambda *a: time.strftime("%Y-%m-%d"),
        # 'department_id': lambda self, cr, uid, context: context.get('c_department_id', False) or context.get('department_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context).context_department_id.id,  MIGRACION: El campo context_department_id no existe
    }

fleet_expense()
