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
from odoo import models, fields, _
from odoo.exceptions import UserError
import time
import calendar


class DistributeFleetExpense(models.TransientModel):

    _name = "distribute.fleet.expense"

    month = fields.Selection([
        ('01','January'), ('02','February'),
        ('03','March'), ('04','April'),
        ('05','May'), ('06','June'),
        ('07','July'), ('08','August'),
        ('09','September'), ('10','October'),
        ('11','November'), ('12','December')],'Month', required=True)
    name = fields.Char('Name',size=64,required=True)
    year = fields.Integer('Year', required=True, default=lambda r: int(time.strftime("%Y")))


    def distribute_costs(self):
        first_day, last_day = calendar.monthrange(int(self.year),int(self.month))
        user = self.env.user
        for vehicle in self.env['fleet'].search(['|',('company_id','=',user.company_id.id),('analytic_plan_id.company_id', '=', user.company_id.id)]):
            expense_ids = self.env['fleet.expense'].search([('expense_date','>=',str(self.year)+"-"+self.month+"-01"),('expense_date','<=',str(self.year)+"-"+self.month+"-"+str(last_day)),('fleet_id','=',vehicle.id),('distribute','=',True)])
            amount_totals = {}
            for expense in expense_ids:
                if amount_totals.get(expense.expense_type, False):
                    amount_totals[expense.expense_type] += (expense.net_amount or 0.0)
                else:
                    amount_totals[expense.expense_type] = (expense.net_amount or 0.0)

            for expense_type in amount_totals:
                if vehicle.analytic_plan_id:
                    a = expense_type.product_id.product_tmpl_id.property_account_expense.id
                    if not a:
                        a = expense_type.product_id.categ_id.property_account_expense_categ.id
                        if not a:
                            raise osv.except_osv(_('Bad Configuration !'),
                                    _('No product and product category expense property account defined on the related product.\nFill these on product form.'))
                    for line in vehicle.analytic_plan_id.account_ids:
                        amt=line.rate and amount_totals[expense_type] * (line.rate/100) or line.fix_amount

                        al_vals={
                           'name': self.name + u", " + expense_type.name + u": " + vehicle.name,
                           'date': str(self.year)+"-"+self.month+"-"+str(last_day),
                           'account_id': line.analytic_account_id.id,
                           'unit_amount': 1,
                           'product_id': expense_type.product_id.id,
                           'product_uom_id': expense_type.product_id.uom_id.id,
                           'amount': -(amt),
                           'company_id': user.company_id.id,
                           'general_account_id': a,
                           'tag_ids': [(4, line.plan_id.tag_id and line.plan_id.tag_id.id or self.env['account.analytic.journal'].search([('name','=','Gasoil')])[0].id)],
                           'ref': vehicle.license_plate,
                           'department_id': line.department_id and line.department_id.id or False,
                           'delegation_id': line.delegation_id and line.delegation_id.id or False,
                           'manager_id': line.manager_id and line.manager_id.id or False
                        }
                        self.env['account.analytic.line'].create(cr, uid, al_vals, context=context)
                else:
                    moves = self.env['stock.service.picking.line'].sudo().search([('transport_date','>=',str(self.year)+"-"+self.month+"-01"),('transport_date','<=',str(self.year)+"-"+self.month+"-"+str(last_day)),('vehicle_id','=',vehicle.id)])
                    total_hours = sum(moves.mapped('total_hours'))
                    for move in moves:
                        expense = self.env['fleet.expense.type'].sudo().with_context(company_id=move.picking_id.analytic_acc_id.company_id.id).browse(expense_type.id)
                        a = expense.product_id.product_tmpl_id.property_account_expense_id.id
                        if not a:
                            a = expense.product_id.categ_id.property_account_expense_categ_id.id
                            if not a:
                                raise UserError(_('No product and product category expense property account defined on the related product.\nFill these on product form.'))

                        amt = (amount_totals[expense] * move.total_hours) / total_hours
                        al_vals={
                           'name': self.name + u", " + expense.name + u": " + vehicle.name,
                           'date': str(self.year)+"-"+self.month+"-"+str(last_day),
                           'account_id': move.picking_id.analytic_acc_id.id,
                           'unit_amount': move.total_hours,
                           'amount': -(amt),
                           'general_account_id': a,
                           'tag_ids': [(4, self.env['account.analytic.tag'].search([('name','=','Gasoil')])[0].id)],
                           'ref': vehicle.license_plate,
                           'company_id': move.picking_id.analytic_acc_id.company_id.id,
                           'department_id': move.picking_id.analytic_acc_id.department_id and move.picking_id.analytic_acc_id.department_id.id or False,
                           'delegation_id': move.picking_id.analytic_acc_id.delegation_id and move.picking_id.analytic_acc_id.delegation_id.id or False,
                           'manager_id': move.picking_id.analytic_acc_id.manager_id and move.picking_id.analytic_acc_id.manager_id.id or False,
                        }
                        self.env['account.analytic.line'].sudo().create(al_vals)

        return {'type': 'ir.actions.act_window_close'}
