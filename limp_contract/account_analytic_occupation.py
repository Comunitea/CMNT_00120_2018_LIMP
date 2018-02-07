# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

"""Extends this object with specific fields to Limpergal"""

from osv import osv, fields

class account_analytic_occupation(osv.osv):
    """Extends this object with specific fields to Limpergal"""

    _inherit = 'account.analytic.occupation'

    def _get_customer_contact_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        hom_help_obj = self.pool.get('limp.contract.line.home.help')
        for occupation in self.browse(cr, uid, ids):
            res[occupation.id] = False
            home_line_ids = hom_help_obj.search(cr, uid, [('analytic_acc_id', '=', occupation.analytic_account_id.id)])
            if home_line_ids:
                line = hom_help_obj.browse(cr, uid, home_line_ids[0])
                if line.customer_contact_id:
                    res[occupation.id] = line.customer_contact_id.id
        return res

    def _search_customer_contact(self, cr, uid, obj, name, args, context=None):
        contact_ids = self.pool.get('res.partner.contact').search(cr, uid, ['|',('name', args[0][1], args[0][2]),('first_name', args[0][1], args[0][2])])
        home_line_ids = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('customer_contact_id', 'in', contact_ids)])
        analytic_acc_ids = [x.analytic_acc_id.id for x in self.pool.get('limp.contract.line.home.help').browse(cr, uid, home_line_ids)]
        ids = self.search(cr, uid, [('analytic_account_id', 'in', analytic_acc_ids)])
        return [('id', 'in', ids)]

    _columns = {
        'occupation_name_id': fields.many2one('account.analytic.occupation.name', "Description", required=True),
        'department_id': fields.many2one("hr.department", "Department"),
        'delegation_id': fields.many2one("res.delegation", "Delegation"),
        'state_id': fields.many2one('res.country.state', 'State'),
        'location_id': fields.many2one('city.council', 'Council'),
        'task_ids': fields.many2many('limp.contract.task', 'account_analytic_occupation_contract_task_rel', 'occupation_id', 'task_id', 'Tasks'),
        'state': fields.selection([('draft', 'Draft'), ('active', 'Active'), ('incidence', 'Based of incidence'), ('replaced', 'Replaced'), ('replacement', 'Replacement'), ('cancelled', 'Cancelled')], 'State', readonly=True),
        #'region_id': fields.many2one('res.country.region', 'Autonomous'), MIGRACION: Region eliminado
        'customer_contact_id': fields.function(_get_customer_contact_id, method=True, relation='res.partner', string='User', readonly=True, type="many2one", fnct_search=_search_customer_contact)
    }

    _defaults = {
        'delegation_id': lambda self, cr, uid, context: context.get('c_delegation_id', False) or context.get('delegation_id', False),
        'department_id': lambda self, cr, uid, context: context.get('c_department_id', False) or context.get('department_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context).context_department_id.id,
        'state': 'draft',
        # 'company_id': lambda self, cr, uid, context: context.get('company_id', False) or self.pool.get('res.users').browse(cr, uid, uid).company_id.id,  MIGRACION: El campo context_department_id no existe
    }

    def create(self, cr, uid, vals, context=None):
        """Fill department field if isn't set"""
        if context is None: context = {}

        if vals.get('analytic_account_id', False):
            account = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_account_id'])
            if not vals.get('delegation_id', False):
                vals['delegation_id'] = account.delegation_id and account.delegation_id.id or False
            if not vals.get('department_id', False):
                vals['department_id'] = account.department_id and account.department_id.id or False
            if not vals.get('company_id', False):
                vals['company_id'] = account.company_id and account.company_id.id or False
            if not vals.get('state_id', False):
                vals['state_id'] = account.state_id and account.state_id.id or False
            if not vals.get('location_id', False):
                vals['location_id'] = account.location_id and account.location_id.id or False
            if not vals.get('region_id', False):
                vals['region_id'] = account.region_id and account.region_id.id or False

        if vals.get('occupation_name_id'):
            vals['description'] = self.pool.get('account.analytic.occupation.name').browse(cr, uid, vals["occupation_name_id"]).name
        return super(account_analytic_occupation, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if vals.get('occupation_name_id'):
            vals['description'] = self.pool.get('account.analytic.occupation.name').browse(cr, uid, vals["occupation_name_id"]).name

        if vals.get('analytic_account_id', False):
            account = self.pool.get('account.analytic.account').browse(cr, uid, vals['analytic_account_id'])
            if not vals.get('delegation_id', False):
                vals['delegation_id'] = account.delegation_id and account.delegation_id.id or False
            if not vals.get('department_id', False):
                vals['department_id'] = account.department_id and account.department_id.id or False
            if not vals.get('company_id', False):
                vals['company_id'] = account.company_id and account.company_id.id or False
            if not vals.get('state_id', False):
                vals['state_id'] = account.state_id and account.state_id.id or False
            if not vals.get('location_id', False):
                vals['location_id'] = account.location_id and account.location_id.id or False
            if not vals.get('region_id', False):
                vals['region_id'] = account.region_id and account.region_id.id or False

        return super(account_analytic_occupation, self).write(cr, uid, ids, vals, context=context)

account_analytic_occupation()
