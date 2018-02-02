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

from osv import osv, fields
from tools.translate import _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


class maintenance_task(osv.osv):

    _name = "maintenance.task"

    def _get_next_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids):
            if not task.last_execution_date:
                initial_date = datetime.strptime(task.start_date, "%Y-%m-%d")
            else:
                initial_date = datetime.strptime(task.last_execution_date, "%Y-%m-%d")

            if task.interval == "3":
                exec_date = (initial_date + relativedelta(days=task.interval_count)).strftime('%Y-%m-%d')
            elif task.interval == "2":
                exec_date = (initial_date + relativedelta(weeks=task.interval_count)).strftime('%Y-%m-%d')
            else:
                exec_date = (initial_date + relativedelta(months=task.interval_count)).strftime('%Y-%m-%d')

            if not task.end_date or task.end_date >= exec_date:
                res[task.id] = exec_date
            else:
                res[task.id] = False

        return res

    _columns = {
        'name': fields.char('Description', size=255, required=True),
        'last_execution_date': fields.date('Last execution date'),
        'start_date': fields.date('Start date', required=True),
        'end_date': fields.date('End date'),
        'interval': fields.selection([('3', 'Daily'),('1', 'Monthly'),('2', 'Weekly')], 'Interval', required=True),
        'interval_count': fields.integer('Repeat each', help="Repeat with interval (Days/Week/Month)", required=True),
        'contract_line_id': fields.many2one('account.analytic.account', 'Workcenter'),
        'contract_id': fields.many2one('account.analytic.account', 'Contract', required=True, readonly=True),
        'next_execution_date': fields.function(_get_next_date, method=True, type="date", string="Next execution date", readonly=True),
        'picking_ids': fields.one2many('stock.service.picking', 'maintenace_task_id', string="Picking history", readonly=True)
    }

    _defaults = {
        "interval": "1",
        "interval_count": 1
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        for obj in self.browse(cr, uid, ids):
            if not 'last_execution_date' in vals or vals['last_execution_date'] != False:
                if vals.get('end_date', False) and vals.get('last_execution_date', obj.last_execution_date) > vals['end_date']:
                    raise osv.except_osv('Error', u'No puede poner un fecha fin a una tarea de mantenimiento anterior a la fecha de última ejecución, si tiene que ser así escriba manualmente una fecha de última ejecución anterior y recuerde eliminar el albarán de mantenimiento que ya debe estar generado con una fecha posterior a la de finalización')
        return super(maintenance_task, self).write(cr, uid, ids, vals, context=context)

    def execute_maintenace(self, cr, uid, ids, context=None):
        if context is None: context = {}
        now = datetime.today()
        to_compare = now + relativedelta(days=45)
        to_compare = to_compare.strftime('%Y-%m-%d')
        domain = [('contract_id.state', '=', "open"), '|', ('end_date', '=', False), ('end_date', '>=', to_compare), '|', ('last_execution_date', '=', False), ('last_execution_date', '<=', to_compare)]
        if ids:
            domain.append(('id', 'in', ids))
        tasks_to_execute_ids = self.search(cr, uid, domain)
        end_tasks = []
        while(tasks_to_execute_ids):
            for task in self.browse(cr, uid, tasks_to_execute_ids, context):
                if task.next_execution_date and task.next_execution_date <= to_compare:
                    contract_id = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', task.contract_id.id)])[0]
                    contract = self.pool.get('limp.contract').browse(cr, uid, contract_id)
                    self.pool.get('stock.service.picking').create(cr, uid, {
                        'picking_type': 'sporadic',
                        'planified': True,
                        'maintenance': True,
                        'contract_id': contract_id,
                        'picking_date': task.next_execution_date,
                        'payment_type': contract.payment_type_id and contract.payment_type_id.id or False,
                        'payment_term': contract.payment_term_id and contract.payment_term_id.id or False,
                        'invoice_type': "noinvoice",
                        'ccc_account_id': contract.bank_account_id and contract.bank_account_id.id or False,
                        'manager_id': (task.contract_line_id and task.contract_line_id.manager_id) and task.contract_line_id.manager_id.id or contract.analytic_account_id.manager_id.id,
                        'partner_id': contract.partner_id.id,
                        'pricelist_id': contract.partner_id.property_product_pricelist.id,
                        'address_invoice_id': contract.address_invoice_id.id,
                        'department_id': (task.contract_line_id and task.contract_line_id.department_id) and task.contract_line_id.department_id.id or contract.analytic_account_id.department_id.id,
                        'delegation_id': (task.contract_line_id and task.contract_line_id.delegation_id) and task.contract_line_id.delegation_id.id or contract.analytic_account_id.delegation_id.id,
                        'description': task.name,
                        'address_id': contract.address_id.id,
                        'no_quality': contract.no_quality,
                        'maintenace_task_id': task.id,
                        'parent_id': task.contract_line_id and task.contract_line_id.id or contract.analytic_account_id.id,
                    })
                    task.write({'last_execution_date': task.next_execution_date})
                else:
                    end_tasks.append(task.id)

            domain2 = list(domain)
            if end_tasks:
                domain2.append(('id', 'not in', end_tasks))

            tasks_to_execute_ids = self.search(cr, uid, domain2)
        return True

maintenance_task()

class account_analytic_account(osv.osv):

    _inherit = "account.analytic.account"

    _columns = {
        'maintenance_task_ids': fields.one2many('maintenance.task', 'contract_id', string='Maintenance tasks')
    }

account_analytic_account()

class stock_service_picking(osv.osv):

    _inherit = "stock.service.picking"


    _columns = {
        'maintenace_task_id': fields.many2one('maintenance.task', 'Maintenance task', readonly=True)
    }

stock_service_picking()
