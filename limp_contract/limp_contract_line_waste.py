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

"""Extension of Limpergal's contract lines for waste case"""

from openerp import models, fields
from tools.translate import _

class limp_contract_line_waste(models.Model):
    """Extension of Limpergal's contract lines for waste case"""

    _name = "limp.contract.line.waste"
    _description = "Limpergal's contract lines for waste"
    _inherits = {'limp.contract.line': "contract_line_id", 'account.analytic.account': 'analytic_acc_id'}

    _columns = {
        'contract_line_id': fields.many2one('limp.contract.line', 'Contract line', readonly=True, required=True, ondelete="cascade"), # MIGRACION: ondelete
        'analytic_acc_id': fields.many2one('account.analytic.account', 'Analytic account', readonly=True, required=True, ondelete="cascade"), # MIGRACION: ondelete
        'picking_line_ids': fields.one2many('stock.service.picking', 'contract_line_id', 'Pickings'),
    }

    _defaults = {
        'delegation_id': lambda s, cr, uid, c: c.get('c_delegation_id', False) or s.pool.get('res.users').browse(cr, uid, uid).context_delegation_id.id,
        'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
        'parent_id': lambda self, cr, uid, context: context.get('parent_id', False),
        'company_id': lambda self, cr, uid, context: context.get('company_id', False),
        # 'department_id': lambda self, cr, uid, context: context.get('c_department_id', False) or context.get('department_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context).context_department_id.id,  MIGRACION: El campo context_department_id no existe
    }

    def open_line(self, cr, uid, ids, context=None):
        if context is None: context = {}
        return self.write(cr, uid, ids, {'state': 'open'})

    def reopen_line(self, cr, uid, ids, context=None):
        if context is None: context = {}
        return self.write(cr, uid, ids, {'state': 'open'})

    def create(self, cr, uid, vals, context=None):
        """Creates a sequence in contract as line num"""
        if context is None: context = {}
        if vals.get('contract_id', False):
            contract = self.pool.get('limp.contract').browse(cr, uid, vals['contract_id'])
            partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
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
                if not vals.get('state_id', False):
                    vals['state_id'] = partner.address_get()['default'] and self.pool.get('res.partner.address').browse(cr, uid, partner.address_get()['default']).state_id and self.pool.get('res.partner.address').browse(cr, uid, partner.address_get()['default']).state_id.id or False
                if not vals.get('location_id', False):
                    vals['location_id'] = partner.address_get()['default'] and self.pool.get('res.partner.address').browse(cr, uid, partner.address_get()['default']).location_id and self.pool.get('res.partner.address').browse(cr, uid, partner.address_get()['default']).location_id.id or False
                if not vals.get('region_id', False):
                    vals['region_id'] = partner.address_get()['default'] and self.pool.get('res.partner.address').browse(cr, uid, partner.address_get()['default']).region and self.pool.get('res.partner.address').browse(cr, uid, partner.address_get()['default']).region.id or False
        else:
            raise osv.except_osv(_('Error!'), _('Not contract defined for this line'))

        return super(limp_contract_line_waste, self).create(cr, uid, vals, context=context)

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

        res = super(limp_contract_line_waste, self).unlink(cr, uid, ids, context=context)
        self.pool.get('limp.contract.line').unlink(cr, uid, lines_to_delete, context=context)
        self.pool.get('account.analytic.account').unlink(cr, uid, account_to_delete, context=context)

        return res

limp_contract_line_waste()

class stock_service_picking(models.Model):

    _inherit = "stock.service.picking"

    _columns = {
        'contract_line_id': fields.many2one('limp.contract.line.waste', 'Contract line'),
    }

    def create(self, cr, uid, vals, context=None):
        """If contract_line_id is defined, it fills analytic_account field"""
        if context is None: context = {}
        if vals.get('contract_line_id', False):
            line = self.pool.get('limp.contract.line.waste').browse(cr, uid, vals['contract_line_id'])
            vals['analytic_acc_id'] = line.analytic_acc_id and line.analytic_acc_id.id or False

        return super(stock_service_picking, self).create(cr, uid, vals, context=context)

stock_service_picking()
