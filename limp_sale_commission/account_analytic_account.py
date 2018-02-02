# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'

    def create_concept_invoice_line(self, cr, uid, analytic, concept, invoice_id, end_date, context=None):
        """creates an invoice line for concept in args"""
        if context is None: context = {}

        res = super(account_analytic_account, self).create_concept_invoice_line(cr, uid, analytic, concept, invoice_id, end_date, context=context)
        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        
        contract_ids = self.pool.get('limp.contract').search(cr, uid, ['|',('analytic_account_id','=', analytic.id),('analytic_account_id','=', analytic.parent_id.id)])
        if res and contract_ids:
            contract = self.pool.get('limp.contract').browse(cr,uid, contract_ids[0])
            invoiced = False
            if contract.contract_agent_ids:
                for agent_id in contract.contract_agent_ids:
                    inv_line = self.pool.get('account.invoice.line').browse(cr, uid, res)
                    for invoice in contract.invoice_ids:
                        if invoice.date_invoice != invoice_obj.date_invoice:
                            invoiced = True
                            break
                    
                    if agent_id.invoice_settle == 'all_invoice' or (agent_id.invoice_settle == 'first_invoice' and (not contract.invoice_ids or invoiced==False)):
                        if inv_line.product_id and inv_line.product_id.commission_exent != True:
                            vals = {
                                'invoice_line_id': inv_line.id,
                                'agent_id': agent_id.agent_id.id,
                                'commission_id': agent_id.commission_id.id,
                                'settled': False
                            }
                            line_agent_id = self.pool.get('invoice.line.agent').create(cr, uid, vals)
                            self.pool.get('invoice.line.agent').calculate_commission(cr, uid, [line_agent_id])
        return res 

account_analytic_account()
