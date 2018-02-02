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

from osv import osv, fields
import time
import calendar
from tools.translate import _

class distribute_fleet_expense(osv.osv_memory):

    _name = "distribute.fleet.expense"

    _columns = {
        'month': fields.selection([
            ('01','January'), ('02','February'),
            ('03','March'), ('04','April'),
            ('05','May'), ('06','June'),
            ('07','July'), ('08','August'),
            ('09','September'), ('10','October'),
            ('11','November'), ('12','December')],'Month', required=True),
        'name': fields.char('Name',size=64,required=True),
        'year': fields.integer('Year', required=True)
    }

    _defaults = {
        'year': lambda *a: int(time.strftime("%Y"))
    }

    def distribute_costs(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        analytic_line_obj = self.pool.get('account.analytic.line')
        picking_line_obj = self.pool.get('stock.service.picking.line')
        first_day, last_day = calendar.monthrange(int(obj.year),int(obj.month))
        user = self.pool.get('res.users').browse(cr, uid, uid)
        for vehicle in self.pool.get('fleet').browse(cr, uid, self.pool.get('fleet').search(cr, uid, ['|',('company_id','=',user.company_id.id),('analytic_plan_id.company_id', '=', user.company_id.id)])):
            expense_ids = self.pool.get('fleet.expense').search(cr, uid, [('expense_date','>=',str(obj.year)+"-"+obj.month+"-01"),('expense_date','<=',str(obj.year)+"-"+obj.month+"-"+str(last_day)),('fleet_id','=',vehicle.id),('distribute','=',True)])
            amount_totals = {}
            for expense in self.pool.get('fleet.expense').browse(cr, uid, expense_ids):
                if amount_totals.get(expense.expense_type.id, False):
                    amount_totals[expense.expense_type.id] += (expense.net_amount or 0.0)
                else:
                    amount_totals[expense.expense_type.id] = (expense.net_amount or 0.0)

            for expense_type in amount_totals:
                if vehicle.analytic_plan_id:
                    expense_obj = self.pool.get('fleet.expense.type').browse(cr, uid, expense_type)
                    a = expense_obj.product_id.product_tmpl_id.property_account_expense.id
                    if not a:
                        a = expense_obj.product_id.categ_id.property_account_expense_categ.id
                        if not a:
                            raise osv.except_osv(_('Bad Configuration !'),
                                    _('No product and product category expense property account defined on the related product.\nFill these on product form.'))
                    for line in vehicle.analytic_plan_id.account_ids:
                        amt=line.rate and amount_totals[expense_type] * (line.rate/100) or line.fix_amount

                        al_vals={
                           'name': obj.name + u", " + expense_obj.name + u": " + vehicle.name,
                           'date': str(obj.year)+"-"+obj.month+"-"+str(last_day),
                           'account_id': line.analytic_account_id.id,
                           'unit_amount': 1,
                           'product_id': expense_obj.product_id.id,
                           'product_uom_id': expense_obj.product_id.uom_id.id,
                           'amount': -(amt),
                           'company_id': user.company_id.id,
                           'general_account_id': a,
                           'journal_id': line.plan_id.journal_id and line.plan_id.journal_id.id or self.pool.get('account.analytic.journal').search(cr, uid, [('name','=','Gasoil')])[0],
                           'ref': vehicle.license_plate,
                           'department_id': line.department_id and line.department_id.id or False,
                           'delegation_id': line.delegation_id and line.delegation_id.id or False,
                           'manager_id': line.manager_id and line.manager_id.id or False
                        }
                        analytic_line_obj.create(cr, uid, al_vals, context=context)
                else:
                    move_ids = picking_line_obj.search(cr, 1, [('transport_date','>=',str(obj.year)+"-"+obj.month+"-01"),('transport_date','<=',str(obj.year)+"-"+obj.month+"-"+str(last_day)),('vehicle_id','=',vehicle.id)])
                    total_hours = 0.0
                    for move in picking_line_obj.browse(cr, 1, move_ids):
                        total_hours += move.total_hours
                    for move in picking_line_obj.browse(cr, 1, move_ids):
                        expense_obj = self.pool.get('fleet.expense.type').browse(cr, 1, expense_type, context={'company_id': move.picking_id.analytic_acc_id.company_id.id})
                        a = expense_obj.product_id.product_tmpl_id.property_account_expense.id
                        if not a:
                            a = expense_obj.product_id.categ_id.property_account_expense_categ.id
                            if not a:
                                raise osv.except_osv(_('Bad Configuration !'),
                                        _('No product and product category expense property account defined on the related product.\nFill these on product form.'))

                        amt = (amount_totals[expense_type] * move.total_hours) / total_hours
                        al_vals={
                           'name': obj.name + u", " + expense_obj.name + u": " + vehicle.name,
                           'date': str(obj.year)+"-"+obj.month+"-"+str(last_day),
                           'account_id': move.picking_id.analytic_acc_id.id,
                           'unit_amount': move.total_hours,
                           'amount': -(amt),
                           'general_account_id': a,
                           'journal_id': self.pool.get('account.analytic.journal').search(cr, uid, [('name','=','Gasoil')])[0],
                           'ref': vehicle.license_plate,
                           'company_id': move.picking_id.analytic_acc_id.company_id.id,
                           'department_id': move.picking_id.analytic_acc_id.department_id and move.picking_id.analytic_acc_id.department_id.id or False,
                           'delegation_id': move.picking_id.analytic_acc_id.delegation_id and move.picking_id.analytic_acc_id.delegation_id.id or False,
                           'manager_id': move.picking_id.analytic_acc_id.manager_id and move.picking_id.analytic_acc_id.manager_id.id or False,
                        }
                        analytic_line_obj.create(cr, 1, al_vals, context=context)

        return {'type': 'ir.actions.act_window_close'}


distribute_fleet_expense()
