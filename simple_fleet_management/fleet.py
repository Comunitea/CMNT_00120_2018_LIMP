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

from osv import osv, fields
from tools.translate import _


class fleet(osv.osv):
    """Model to manage vehicles"""

    _name = "fleet"
    _description = "Fleet"

    def _get_current_user_company(self, cr, uid, context={}):
        """
            Obtiene la compañía del usuario activo
        """
        current_user = self.pool.get('res.users').browse(cr, uid, uid)
        return current_user.company_id.id

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for vehicle in self.browse(cr, uid, ids, context=context):
            res.append((vehicle.id, vehicle.license_plate))
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        """allows search by center name too"""
        if args is None:
            args = []
        if context is None:
            context = {}

        if name:
            ids = self.search(cr, user, ['|', ('license_plate', operator, name), ('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)

        result = self.name_get(cr, user, ids, context)
        return result

    def _get_avg_consumption(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        domain = []
        action_model, type_expense_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'simple_fleet_management', 'fleet_expense_type_refueling')

        if context.get('start_date', False):
            domain.append(('expense_date', '>=', context['start_date']))
        if context.get('end_date', False):
            domain.append(('expense_date', '<=', context['end_date']))

        for fleet in self.browse(cr, uid, ids):
            if domain:
                domain2 = [('expense_type', '=', type_expense_id),
                           ('fleet_id', '=', fleet.id)]
                domain2.extend(domain)
                expense_ids = self.pool.get('fleet.expense').search(cr, uid, domain2)
                consumption_total = 0.0
                expense_without_cosumption = []
                for expense in self.pool.get('fleet.expense').browse(cr, uid, expense_ids):
                    if expense.consumption:
                        consumption_total += expense.consumption
                    else:
                        expense_without_cosumption.append(expense.id)

                if expense_ids and len(expense_ids) != len(expense_without_cosumption):
                    res[fleet.id] = consumption_total / (len(expense_ids) - len(expense_without_cosumption))
                else:
                    res[fleet.id] = 0.0
            else:
                res[fleet.id] = 0.0

        return res


    _columns = {
        'type': fields.selection([('truck', 'Truck'), ('car', 'Car'), ('van', 'Van'), ('other', 'Other')], "Type", required=True, help="Vehicle type"),
        'name': fields.char('Name', size=128, required=True),
        'license_plate': fields.char('License plate', size=18, required=True),
        'note': fields.text('Description'),
        'expense_ids': fields.one2many('fleet.expense', 'fleet_id', 'Expenses', domain=[('distribute','=',True)]),
        'expense_no_distribute_ids': fields.one2many('fleet.expense', 'fleet_id', 'No Distribute expenses', domain=[('distribute','=',False)]),
        'active': fields.boolean('Active'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'avg_consumption': fields.function(_get_avg_consumption, method=True, string="Average consumption", type="float", readonly=True),
        'start_date': fields.dummy(string='Start date', type='date'),
        'end_date': fields.dummy(string='En date', type='date')
    }

    _defaults = {
        'type': 'truck',
        'active': True,
        'company_id': lambda self, cr, uid, context: self._get_current_user_company(cr, uid, context),
    }

    _sql_constraints = [
        ('license_plate_uniq', 'unique (license_plate)', _(
            'The license plate must be unique !')),
    ]

fleet()
