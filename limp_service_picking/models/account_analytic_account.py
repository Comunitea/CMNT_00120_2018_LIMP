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

from odoo import models, fields


class analytic_account_employees(models.Model):

    _name = "analytic.account.employees"
    _auto = False

    analytic_id = fields.Many2one("account.analytic.account", "Analytic", readonly=True)
    employee_id = fields.Many2one("hr.employee", "Employee", readonly=True)
    hours = fields.Float("Hours", readonly=True)
    extra_hours = fields.Float("Hours", readonly=True)

    def init(self):
        self.env.cr.execute("""
            create or replace view analytic_account_employees as (
            SELECT min(id) as id, employee_id, analytic_id,
            sum(hours) as hours, sum(extra_hours) as extra_hours
            FROM timesheet GROUP BY analytic_id, employee_id
            )""")


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    '''def _get_distinct_employee_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for acc in self.browse(cr, uid, ids, context=context):
            employee_ids = []
            timesheet_ids = []

            for timesheet in acc.employee_ids:
                if timesheet.employee_id.id not in employee_ids:
                    employee_ids.append(timesheet.employee_id.id)
                    timesheet_ids.append(timesheet.id)
            res[acc.id] = timesheet_ids

        return res'''


    employee_ids = fields.One2many('timesheet', 'analytic_id', string='Timesheet', copy=False)
    active_employee_ids = fields.One2many('timesheet', 'analytic_id', 'Active timesheets', domain=[('old','=',False)], copy=False)
    inactive_employee_ids = fields.One2many('timesheet', 'analytic_id', 'Unactive timesheets', domain=[('old','=',True)], copy=False)
    report_employee_ids = fields.One2many("analytic.account.employees", "analytic_id", string='Timesheet', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=False, change_default=True, default=lambda r: r._context.get('company_id', r.env.user.company_id.id))
    delegation_id = fields.Many2one(
        'res.delegation', 'Delegation', change_default=True,
        default=lambda r: r._context.get('c_delegation_id', r._context.get('delegation_id', r.env.user.context_delegation_id.id)))
    other_expense_ids = fields.One2many('stock.service.other.expenses', 'analytic_id', string="Other expenses", copy=False)
    address_invoice_id = fields.Many2one('res.partner', 'Address invoice')
    date_start = fields.Date('Date start')
    date = fields.Date('Date end')
    contact_id = fields.Many2one('res.partner', 'Contact')
    description = fields.Char('Service', size=255, required=True)
    address_id = fields.Many2one('res.partner', 'Address')
