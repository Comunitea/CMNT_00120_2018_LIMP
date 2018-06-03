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
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeReplacementWzd(models.TransientModel):

    _name = "employee.replacement.wzd"

    @api.model
    def _get_default_employee(self):
        remuneration_ids = self._context.get('active_ids', [])
        if remuneration_ids:
            remuneration_obj = self.env['remuneration'].browse(remuneration_ids[0])
            return remuneration_obj.employee_id.id

    @api.model
    def _get_default_location(self):
        remuneration_ids = self._context.get('active_ids', [])
        if remuneration_ids:
            remuneration_obj = self.env['remuneration'].browse(remuneration_ids[0])
            return remuneration_obj.location_id.id

    @api.model
    def _get_default_department(self):
        remuneration_ids = self._context.get('active_ids', [])
        if remuneration_ids:
            remuneration_obj = self.env['remuneration'].browse(remuneration_ids[0])
            if remuneration_obj.department_id:
                return remuneration_obj.department_id.id
        return False

    employee_id = fields.Many2one('hr.employee', 'Substitute')
    conditions = fields.Selection(
        [('equal_condition', 'Equal conditions'),
         ('diff_condition', 'Different conditions')],
        required=True, default='equal_condition')
    with_contract = fields.Boolean()
    contract_hours = fields.Float('Hours', digits=(12, 2))
    with_hour_price = fields.Boolean()
    hour_price_hours = fields.Float('Hours', digits=(12, 2))
    with_fix_qty = fields.Boolean()
    price = fields.Float(digits=(12, 2))
    quantity = fields.Float(digits=(12, 2))
    ss_hours = fields.Float('SS hours', digits=(4, 2))
    ss_no_hours = fields.Float('No ss hours', digits=(4, 2))
    effective = fields.Float(digits=(12, 2))
    distribute_bt_remuneration = fields.Boolean(
        'Distribute between remunerations',
        help="Distribute quantities between all selected"
        "remuneration proportionally to original hours")

    search_employee_ids = fields.Many2many('hr.employee')
    search_employee_id = fields.Many2one('hr.employee',
                                         default=_get_default_employee)
    search_location = fields.Many2one('city.council', 'Council',
                                      default=_get_default_location)
    search_department_id = fields.Many2one('hr.department', 'Department',
                                           default=_get_default_department)

    @api.multi
    def search_replacements(self):
        employee_domain = []
        if self.search_location:
            employee_domain.append(
                ('work_council_id', '=', self.search_location.id))
#        if self.department_id:
#            employee_domain.append(('department_ids', 'in', [self.department_id.id]))
        if self.search_employee_id:
            employee_domain.append(('id', '!=', self.search_employee_id.id))
        self.search_employee_ids = self.env['hr.employee'].search(
            employee_domain)
        return {'type': 'ir.actions.do_nothing'}

        #  for x in self.pool.get('hr.employee').browse(cr, uid, employees):
            #  if x.department_ids:
                #  for y in x.department_ids:
                    #  if y.id == self.department_id.id:
                        #  possible_employees.append(x.id)
        '''real_possible_employees = []
        if possible_employees:
            for employee in self.pool.get('hr.employee').browse(cr, uid, possible_employees):
                total_availability = datetime.strptime(obj.end_date, "%Y-%m-%d") - datetime.strptime(obj.start_date, "%Y-%m-%d")
                total_availability = total_availability.days * 8
                if total_availability < 0:
                    raise osv.except_osv(_('Error!'),_("Incorrect range of dates"))
                occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('employee_id', '=', employee.id), ('state', 'in', ['active','replacement']), ('date', '>=', obj.start_date), ('date', '<=', obj.end_date)])
                total_occupation = 0.0
                for occupation in self.pool.get('account.analytic.occupation').browse(cr, uid, occupation_ids):
                    total_occupation += occupation.duration

                if total_availability >= total_occupation + obj.hour_no:
                    real_possible_employees.append(employee.id)

        obj.write({'employee_ids': [(6, 0, real_possible_employees)]})'''

    @api.multi
    def action_replace(self):
        if not self.employee_id:
            raise UserError(_("You must set substitute"))
        remuneration_ids = self._context.get('active_ids', [])

        if remuneration_ids:
            remuneration_objs = self.env['remuneration'].browse(
                remuneration_ids)
            total_ss_hours = sum([x.ss_hours for x in remuneration_objs])
            total_noss_hours = sum([x.ss_no_hours for x in remuneration_objs])
            total_hours = (total_ss_hours + total_noss_hours)

            for line_remuneration in remuneration_objs:
                if not line_remuneration.incidence:
                    raise UserError(_('You must set remuneration as based of incidence for replacing employee'))

                if self.conditions != 'equal_condition' and not \
                        self.distribute_bt_remuneration:
                    with_contract = self.with_contract
                    contract_hours = self.contract_hours
                    with_hour_price = self.with_hour_price
                    hour_price_hours = self.hour_price_hours
                    with_fix_qty = self.with_fix_qty
                    price = self.price
                    quantity = self.quantity
                    ss_hours = self.ss_hours
                    ss_no_hours = self.ss_no_hours
                    effective = self.effective
                elif self.conditions != 'equal_condition':
                    remu_hours = line_remuneration.ss_no_hours + \
                        line_remuneration.ss_hours
                    with_contract = self.with_contract
                    contract_hours = (self.contract_hours * remu_hours) / (
                        total_hours or 1.0)
                    with_hour_price = self.with_hour_price
                    hour_price_hours = (self.hour_price_hours * remu_hours) / (
                        total_hours or 1.0)
                    with_fix_qty = self.with_fix_qty
                    price = self.price
                    quantity = (self.quantity * remu_hours) / (
                        total_hours or 1.0)
                    ss_hours = (self.ss_hours * line_remuneration.ss_hours) / (
                        total_ss_hours or 1.0)
                    ss_no_hours = (self.ss_no_hours *
                                   line_remuneration.ss_no_hours) / (
                        total_noss_hours or 1.0)
                    effective = (self.effective * remu_hours) / (
                        total_hours or 1.0)
                else:
                    with_contract = line_remuneration.with_contract
                    contract_hours = line_remuneration.contract_hours
                    with_hour_price = line_remuneration.with_hour_price
                    hour_price_hours = line_remuneration.hour_price_hours
                    with_fix_qty = line_remuneration.with_fix_qty
                    price = line_remuneration.price
                    quantity = line_remuneration.quantity
                    ss_hours = line_remuneration.ss_hours
                    ss_no_hours = line_remuneration.ss_no_hours
                    effective = line_remuneration.effective

                type_incidence_id = self.env.ref(
                    'analytic_incidences.incidence_replacement').id
                self.env['remuneration'].create(
                    {
                        'employee_id': self.employee_id.id,
                        'date': line_remuneration.date,
                        'analytic_account_id':
                            line_remuneration.analytic_account_id.id,
                        'parent_id': line_remuneration.id,
                        'incidence_id_tp': type_incidence_id,
                        'date_to': line_remuneration.date_to or False,
                        'with_contract': with_contract,
                        'contract_hours': contract_hours,
                        'with_hour_price': with_hour_price,
                        'hour_price_hours': hour_price_hours,
                        'ss_hours': ss_hours,
                        'ss_no_hours': ss_no_hours,
                        'with_fix_qty': with_fix_qty,
                        'price': price,
                        'quantity': quantity,
                        'effective': effective,
                        'incidence': True,
                    })

        return {'type': 'ir.actions.act_window_close'}
