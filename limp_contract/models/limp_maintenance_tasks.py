# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


class MaintenanceTask(models.Model):

    _name = "maintenance.task"

    name = fields.Char('Description', size=255, required=True)
    last_execution_date = fields.Date('Last execution date')
    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date')
    interval = fields.Selection([('3', 'Daily'),('1', 'Monthly'),('2', 'Weekly')], 'Interval', required=True, default='1')
    interval_count = fields.Integer('Repeat each', help="Repeat with interval (Days/Week/Month)", required=True, default=1)
    contract_line_id = fields.Many2one('account.analytic.account', 'Workcenter')
    contract_id = fields.Many2one('account.analytic.account', 'Contract', required=True, readonly=True)
    contract_accounts = fields.Many2many('account.analytic.account', compute='_compute_analytic_accounts')
    next_execution_date = fields.Date('Next execution date', compute='_compute_next_execution_date')
    picking_ids = fields.One2many('stock.service.picking', 'maintenace_task_id', string="Picking history", readonly=True)
    monitoring_situation=fields.Char("Monitoring Situation")
    type_ddd_ids=fields.Many2many('types.ddd', string='Types ddd')

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        # Es necesario sobreescribir el domain ya que falla cuando se crea 1
        # nuevo registro debido a que en el domain xml se recibe el
        # campo funcion como [(0, 0, {...})]
        if self.contract_id:
            return {

             'domain': {

              'contract_line_id':
              [('id', 'in', self.contract_id.get_same_contract_accounts()._ids)
               ]}}

    @api.depends('contract_id')
    def _compute_analytic_accounts(self):
        for task in self.filtered('contract_id'):
            task.contract_accounts = task.contract_id.get_same_contract_accounts()

    def _compute_next_execution_date(self):
        for task in self:
            if not task.last_execution_date:
                initial_date = datetime.strptime(task.start_date, "%Y-%m-%d")
            else:
                initial_date = datetime.strptime(task.last_execution_date, "%Y-%m-%d")

            if not task.last_execution_date:
                exec_date = task.start_date
            elif task.interval == "3":
                exec_date = (initial_date + relativedelta(days=task.interval_count)).strftime('%Y-%m-%d')
            elif task.interval == "2":
                exec_date = (initial_date + relativedelta(weeks=task.interval_count)).strftime('%Y-%m-%d')
            else:
                exec_date = (initial_date + relativedelta(months=task.interval_count)).strftime('%Y-%m-%d')

            if not task.end_date or task.end_date >= exec_date:
                task.next_execution_date = exec_date
            else:
                task.next_execution_date = False

    def write(self, vals):
        for obj in self:
            if not 'last_execution_date' in vals or vals['last_execution_date'] != False:
                if vals.get('end_date', False) and vals.get('last_execution_date', obj.last_execution_date) > vals['end_date']:
                    raise UserError(u'No puede poner un fecha fin a una tarea de mantenimiento anterior a la fecha de última ejecución, si tiene que ser así escriba manualmente una fecha de última ejecución anterior y recuerde eliminar el albarán de mantenimiento que ya debe estar generado con una fecha posterior a la de finalización')
        return super(MaintenanceTask, self).write(vals)

    @api.multi
    def execute_maintenace(self):
        now = datetime.today()
        to_compare = now + relativedelta(days=45)
        to_compare = to_compare.strftime('%Y-%m-%d')
        domain = [('contract_id.state', '=', "open"), '|', ('end_date', '=', False), ('end_date', '>=', to_compare), '|', ('last_execution_date', '=', False), ('last_execution_date', '<=', to_compare)]
        if self._ids:
            domain.append(('id', 'in', self._ids))
        tasks_to_execute_ids = self.search(domain)
        end_tasks = []
        while(tasks_to_execute_ids):
            for task in tasks_to_execute_ids:
                if task.next_execution_date and task.next_execution_date <= to_compare:
                    contract = self.env['limp.contract'].search([('analytic_account_id', '=', task.contract_id.id)])[0]
                    self.env['stock.service.picking'].create({
                        'picking_type': 'sporadic',
                        'planified': True,
                        'maintenance': True,
                        'contract_id': contract.id,
                        'picking_date': task.next_execution_date,
                        'payment_type': contract.payment_type_id and contract.payment_type_id.id or False,
                        'payment_term': contract.payment_term_id and contract.payment_term_id.id or False,
                        'invoice_type': "noinvoice",
                        'ccc_account_id': contract.bank_account_id and contract.bank_account_id.id or False,
                        'manager_id': (task.contract_line_id and task.contract_line_id.manager_id) and task.contract_line_id.manager_id.id or contract.analytic_account_id.manager_id.id,
                        'partner_id': contract.partner_id.id,
                        'address_invoice_id': contract.address_invoice_id.id,
                        'department_id': (task.contract_line_id and task.contract_line_id.department_id) and task.contract_line_id.department_id.id or contract.analytic_account_id.department_id.id,
                        'delegation_id': (task.contract_line_id and task.contract_line_id.delegation_id) and task.contract_line_id.delegation_id.id or contract.analytic_account_id.delegation_id.id,
                        'description': task.name,
                        'address_id': contract.address_id.id,
                        'no_quality': contract.no_quality,
                        'maintenace_task_id': task.id,
                        'parent_id': task.contract_line_id and task.contract_line_id.id or contract.analytic_account_id.id,
                        'monitoring_situation': task.monitoring_situation,
                        'type_ddd_ids': [(6, 0, task.type_ddd_ids.ids)],
                        'tag_ids': [(6, 0, contract.tag_ids.ids)]
                    })
                    task.write({'last_execution_date': task.next_execution_date})
                    end_tasks.append(task.id)
                else:
                    end_tasks.append(task.id)

            domain2 = list(domain)
            if end_tasks:
                domain2.append(('id', 'not in', end_tasks))

            tasks_to_execute_ids = self.search(domain2)
        return True


class AccountAnalyticAccount(models.Model):

    _inherit = "account.analytic.account"

    maintenance_task_ids = fields.One2many('maintenance.task', 'contract_id', string='Maintenance tasks')


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    maintenace_task_id = fields.Many2one('maintenance.task', 'Maintenance task', readonly=True)
