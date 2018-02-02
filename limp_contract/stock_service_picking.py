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

"""Limpergal's service pickings"""

from osv import osv, fields
import decimal_precision as dp

class stock_service_picking(osv.osv):

    _inherit = "stock.service.picking"

    _columns = {
        'contract_id': fields.many2one('limp.contract', 'Contract'),
    }

    def create(self, cr, uid, vals, context=None):
        """Creates a sequence in contract as line num"""
        if context is None: context = {}
        if vals.get('contract_id', False):
            contract = self.pool.get('limp.contract').browse(cr, uid, vals['contract_id'])
            if not vals.get('delegation_id', False):
                vals['delegation_id'] = contract.delegation_id.id
            if not vals.get('department_id', False):
                vals['department_id'] = contract.department_id.id
            if not vals.get('company_id', False):
                vals['company_id'] = contract.company_id.id
            if not vals.get('parent_id', False):
                vals['parent_id'] = contract.analytic_account_id.id

        return super(stock_service_picking, self).create(cr, uid, vals, context=context)

    def onchange_contract_id(self, cr, uid, ids, contract_id):
        res = {}
        if contract_id:
            contract = self.pool.get('limp.contract').browse(cr, uid, contract_id)
            res['value'] = {'parent_id': contract.analytic_account_id.id,
                            'department_id': contract.department_id.id,
                            'delegation_id': contract.delegation_id.id,
                            'partner_id': contract.partner_id.id,
                            'manager_id': contract.manager_id.id,
                            'address_invoice_id': contract.address_invoice_id.id,
                            'address_id': contract.address_id.id,
                            'ccc_account_id': contract.bank_account_id.id,
                            'payment_type': contract.payment_type_id.id,
                            'payment_term': contract.payment_term_id.id,
                            'privacy': contract.privacy,
                            'address_tramit_id': contract.address_tramit_id.id}
        return res

stock_service_picking()

