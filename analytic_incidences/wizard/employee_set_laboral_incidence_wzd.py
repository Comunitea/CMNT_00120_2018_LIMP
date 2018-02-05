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

"""Wizard to set a laboral incidence from an employee's form"""

from openerp import models, fields
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime

class employee_set_laboral_incidence_wzd(models.TransientModel):
    """Wizard to set a laboral incidence from an employee's form"""

    _name = "employee.set.laboral.incidence.wzd"

    def _get_default_employee(self, cr, uid, context=None):
        """returns current location ID"""
        if context is None: context = {}

        if context.get('employee_id', False):
            return int(context['active_id'])
        return False

    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee',required=True),#No se muestra
        'date': fields.date('Date',required=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Account', readonly=True),
        'child_ids': fields.many2one('remuneration','Childs remunerations',readonly=True),
        'parent_id': fields.one2many('child_ids', 'remuneration', 'Remuneration parent', readonly=True),
        'date_to': fields.date('Date to'),
        'incidence_id_tp': fields.many2one('incidence','Type'),
        'absence_id_tp': fields.many2one('absence', 'Type absence'),
        'conditions': fields.selection([('equal_condition', 'Equal conditions'), ('diff_condition', 'Different conditions')], 'Conditions', required=True),
        'with_contract': fields.boolean('With contract'),
        'contract_hours': fields.float('Hours', digits=(12,2)),
        'with_hour_price': fields.boolean('With hour price'),
        'hour_price_hours': fields.float('Hours', digits=(12,2)),
        'with_fix_qty': fields.boolean('With fix qty'),
        'price': fields.float('Price',digits=(12,2)),
        'quantity': fields.float('Quantity',digits=(12,2)),
        'ss_hours': fields.float('SS hours', digits=(4,2)),
        'ss_no_hours': fields.float('No ss hours', digits=(4,2)),
        'effective': fields.float('Effective', digits=(12,2)),
        'distribute_bt_remuneration': fields.boolean('Distribute between remunerations', help="Distribute quantities between all selected remuneration proportionally to original hours")
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'employee_id': _get_default_employee,
        'conditions': 'equal_condition'
    }

    def set_incidence(self, cr, uid, ids, context=None):
        """set incidence state in found occupations"""
        vals = {}
        employees_ids = context.get('active_ids', [])
        if employees_ids:
            obj = self.pool.get('hr.employee').browse(cr, uid, employees_ids[0])

        if context is None:
            context = {}
        for line_child_remu in self.browse(cr,uid,ids):
            action_model,type_incidence_id = self.pool.get('ir.model.data').get_object_reference(cr,uid,'analytic_incidences','incidence_absence')
            vals = {
                'with_contract': line_child_remu.with_contract,
                'contract_hours': line_child_remu.contract_hours,
                'with_hour_price': line_child_remu.with_hour_price,
                'hour_price_hours': line_child_remu.hour_price_hours,
                'ss_hours': line_child_remu.ss_hours,
                'ss_no_hours': line_child_remu.ss_no_hours,
                'with_fix_qty': line_child_remu.with_fix_qty,
                'price': line_child_remu.price,
                'quantity': line_child_remu.quantity,
                'date': line_child_remu.date,
                'incidence_id_tp': type_incidence_id,
                'absence_id_tp': line_child_remu.absence_id_tp.id,
                'date_to': line_child_remu.date_to or False,
                'conditions': line_child_remu.conditions,
                'conditions': line_child_remu.conditions,
                'effective': line_child_remu.effective,
                'distribute_bt_remuneration': line_child_remu.distribute_bt_remuneration
                }

            action_model,type_incidence_normal_id = self.pool.get('ir.model.data').get_object_reference(cr,uid,'analytic_incidences','incidence_normal')
            parent_remuneration_id = self.pool.get('remuneration').search(cr,uid, [('employee_id', '=', obj.id),('incidence_id_tp', '=', type_incidence_normal_id),'|',('date_to','=',False),('date_to','>=',line_child_remu.date)])

            if parent_remuneration_id:
                visited_occupations = self.pool.get('remuneration').make_child_inc_remuneration(cr,uid,parent_remuneration_id,vals)

                self.pool.get('hr.laboral.incidence').create(cr, uid, {'initial_date': line_child_remu.date,
                                                            'end_date': line_child_remu.date_to,
                                                            'motive': line_child_remu.absence_id_tp.id,
                                                            'employee_id': obj.id,
                                                            'occupation_ids': [(6, 0, visited_occupations)]
                                                        })

        result = self.pool.get('ir.model.data')._get_id(cr, uid, 'analytic_incidences', 'action_remuneration_tree')
        id = self.pool.get('ir.model.data').read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = self.pool.get('ir.actions.act_window').read(cr, uid, [id])[0]

        result['domain'] = str([('employee_id', '=', obj.id),('date', '>=', line_child_remu.date),'|', ('date_to', '>=', line_child_remu.date_to), ('date_to', '=', False)])


        return result


employee_set_laboral_incidence_wzd()
