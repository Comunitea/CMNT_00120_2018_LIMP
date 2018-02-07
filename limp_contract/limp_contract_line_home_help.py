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

"""Extension of Limpergal's contract lines for home help case"""

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _

class limp_contract_line_home_help(osv.osv):
    """Extension of Limpergal's contract lines for home help case"""

    _name = "limp.contract.line.home.help"
    _description = "Limpergal's contract lines for home help"
    _inherits = {'limp.contract.line': "contract_line_id", 'account.analytic.account': 'analytic_acc_id'}

    _columns = {
        'contract_line_id': fields.many2one('limp.contract.line', 'Contract line', readonly=True, required=True, ondelete="cascade"),
        'customer_contact_id': fields.many2one('res.partner', 'User', required=True),
        # 'contact_identification_id': fields.related('customer_contact_id', 'identification_no', type="char", size=32, readonly=True, string="ID"), MIGRACION: Pendiente de migrar campos de contact a res.partner
        'beneficiary_amount': fields.float('Beneficiary amount', digits_compute=dp.get_precision('Account')),
        'check_amount': fields.float('Check amount', digits_compute=dp.get_precision('Account')),
        'administration_amount': fields.float('Administration amount', digits_compute=dp.get_precision('Account')),
        'partner_social_worker_id': fields.many2one('res.partner', 'Partner social worker'),
        'analytic_acc_id': fields.many2one('account.analytic.account', 'Analytic account', readonly=True, required=True, ondelete="cascade"),
        'social_worker_id': fields.many2one('hr.employee', 'Social worker')
    }

    _defaults = {
        'delegation_id': lambda s, cr, uid, c: c.get('c_delegation_id', False) or s.pool.get('res.users').browse(cr, uid, uid).context_delegation_id.id,
        'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
        'parent_id': lambda self, cr, uid, context: context.get('parent_id', False),
        'company_id': lambda self, cr, uid, context: context.get('company_id', False),
        # 'department_id': lambda self, cr, uid, context: context.get('c_department_id', False) or context.get('department_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context).context_department_id.id, MIGRACION: El campo context_department_id no existe
    }

    def open_line(self, cr, uid, ids, context=None):
        if context is None: context = {}
        return self.write(cr, uid, ids, {'state': 'open'})

    def reopen_line(self, cr, uid, ids, context=None):
        if context is None: context = {}
        return self.write(cr, uid, ids, {'state': 'open'})

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'state': 'draft',
            'date': False,
            'parent_id': False,
            'line_ids': [],
            'employee_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'report_employee_ids': []
        })

        return super(limp_contract_line_home_help, self).copy(cr, 1, id, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        if not context:
            context = {}
        if context.get('is_contract', False):
            line = self.browse(cr, uid, id)
            if line.date:
                return {}
        default.update({
            'state': 'draft',
            'date': False,
            'parent_id': False,
            'line_ids': [],
            'employee_ids': [],
            'active_employee_ids': [],
            'inactive_employee_ids': [],
            'report_employee_ids': []
        })
        return super(limp_contract_line_home_help, self).copy_data(cr, uid, id, default, context)

    def onchange_customer_contact_id(self, cr, uid, ids, customer_contact_id = False):
        """when changing customer contact set state_if field"""
        if customer_contact_id:
            contact_obj = self.pool.get('res.partner.contact').browse(cr, uid, customer_contact_id)
            vals = {}
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.state_id:
                vals['state_id'] = contact_obj.job_id.address_id.state_id.id
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.location:
                vals['location_id'] = contact_obj.job_id.address_id.location.id
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.region:
                vals['region_id'] = contact_obj.job_id.address_id.region.id
            if contact_obj.job_id and contact_obj.job_id.address_id and contact_obj.job_id.address_id.council_id:
                vals['location_id'] = contact_obj.job_id.address_id.council_id.id

            return {'value': vals}

        return {}

    def create(self, cr, uid, vals, context=None):
        """Creates a sequence in contract as line num"""
        if context is None: context = {}
        if vals.get('contract_id', False):
            contract = self.pool.get('limp.contract').browse(cr, uid, vals['contract_id'])
            if contract.seq_lines_id:
                num = self.pool.get('ir.sequence').get_id(cr, uid, contract.seq_lines_id.id)
                vals['name'] = contract.name + u" - " + num
                vals['num'] = num
                if not vals.get('delegation_id', False):
                    vals['delegation_id'] = contract.delegation_id.id
                if not vals.get('department_id', False):
                    vals['department_id'] = contract.department_id.id
                if not vals.get('company_id', False):
                    vals['company_id'] = contract.company_id.id
                if not vals.get('parent_id', False):
                    vals['parent_id'] = contract.analytic_account_id.id
        else:
            raise osv.except_osv(_('Error!'), _('Not contract defined for this line'))

        vals['invoiceable'] = True

        return super(limp_contract_line_home_help, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """Updates occupations_ids if end_date is set"""
        if context is None: context = {}
        res = super(limp_contract_line_home_help, self).write(cr, uid, ids, vals, context=context)

        if vals.get('date', False) or (vals.get('state', False) and vals['state'] in ('open', 'cancelled')) or vals.get('date_start', False):
            occupation_ids = []
            all_remuneration_ids = []
            remuneration_ids_wo_dateto = []

            for line in self.browse(cr, uid, ids, context=context):
                occupation_ids.extend([x.id for x in line.occupation_ids if not x.end_date])
                all_remuneration_ids.extend([x.id for x in line.remuneration_ids])
                remuneration_ids_wo_dateto.extend([x.id for x in line.remuneration_ids if not x.date_to])

            if occupation_ids:
                occupation_vals = {}
                if vals.get('date', False):
                    occupation_vals['end_date'] = vals['date']
                    occupation_vals['end_type'] = 'end_date'

                if vals.get('state', False):
                    if vals['state'] == 'open':
                        occupation_vals['state'] = 'active'
                    elif vals['state'] == 'cancelled':
                        occupation_vals['state'] = 'cancelled'
                self.pool.get('account.analytic.occupation').write(cr, uid, occupation_ids, occupation_vals)

            if all_remuneration_ids:
                if vals.get('date_start', False):
                    self.pool.get('remuneration').write(cr, 1, all_remuneration_ids, {'date': vals['date_start']})
                if vals.get('date', False) and remuneration_ids_wo_dateto:
                    self.pool.get('remuneration').write(cr, 1, remuneration_ids_wo_dateto, {'date_to': vals['date']})

        return res

    def unlink(self, cr, uid, ids, context=None):
        """delete associated contract_line"""
        if context is None: context = {}
        lines_to_delete = []
        account_to_delete = []

        for line in self.browse(cr, uid, ids, context=context):
            if line.state not in ('draft','cancelled'):
                raise osv.except_osv(_('Error!'),_("Only contract lines in draft or cancelled states can be deleted."))
            lines_to_delete.append(line.contract_line_id.id)
            account_to_delete.append(line.analytic_acc_id.id)

        res = super(limp_contract_line_home_help, self).unlink(cr, uid, ids, context=context)
        self.pool.get('limp.contract.line').unlink(cr, uid, lines_to_delete, context=context)
        self.pool.get('account.analytic.account').unlink(cr, uid, account_to_delete, context=context)

        return res

limp_contract_line_home_help()
