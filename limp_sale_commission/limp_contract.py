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
from osv import osv, fields
from tools.translate import _

class limp_contract_agent(osv.osv):
    _name = 'limp.contract.agent'
    _columns = {
        'contract_id':fields.many2one('limp.contract', 'Contract', required=False, ondelete='cascade', help=''),
        'partner_id': fields.related('contract_id', 'partner_id', type='many2one', relation='res.partner', string="Customer", readonly=True),
        'agent_id':fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id':fields.many2one('commission', 'Applied commission', required=True, ondelete='cascade', help=''),
        'invoice_settle': fields.selection((
            ('first_invoice', 'Only first invoice'),
            ('all_invoice', 'All invoices')), 'Settle', required=True)
    }
    def onchange_agent_id(self, cr, uid, ids, agent_id):
        """al cambiar el agente cargamos sus comisión"""
        result = {}
        v = {}
        if agent_id:
            agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
            v['commission_id'] = agent.commission.id
            v['invoice_settle'] = agent.invoice_settle
        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id=False, commission_id=False):
        """al cambiar la comisión comprobamos la selección"""
        result = {}

        if commission_id:
            partner_commission = self.pool.get('commission').browse(cr, uid, commission_id)
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
                    if agent.commission.id !=  partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        result['warning']['message'] = _('A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
        return result
limp_contract_agent()

class limp_contract(osv.osv):
    _inherit = 'limp.contract'
    _columns = {
        'contract_agent_ids':fields.one2many('limp.contract.agent', 'contract_id', 'Agents', states={'draft': [('readonly', False)]})
    }

    def create(self, cr, uid, values, context=None):
        """
        """
        res = super(limp_contract, self).create(cr, uid, values, context=context)
        if 'contract_agent_ids' in values:
            for contract_agent in values['contract_agent_ids']:
                self.pool.get('limp.contract.agent').write(cr, uid, contract_agent[1], {'contract_id':res})
        return res

    def write(self, cr, uid, ids, values, context=None):
        """
        """

        if 'contract_agent_ids' in values:
            for contract_agent in values['contract_agent_ids']:
                for id in ids:
                    if contract_agent[2]:
                        contract_agent[2]['contract_id']=id
                    else:
                        self.pool.get('limp.contract.agent').unlink(cr, uid, contract_agent[1])
        return super(limp_contract, self).write(cr, uid, ids, values, context=context)

    def onchange_partner_id(self, cr, uid, ids, part):
        """heredamos el evento de cambio del campo partner_id para actualizar el campo agent_id"""
        contract_agent_ids=[]
        res = super(limp_contract, self).onchange_partner_id(cr, uid, ids, part)
        if res.get('value', False) and part:
            limp_contract_agent = self.pool.get('limp.contract.agent')
            if ids:
                limp_contract_agent.unlink(cr, uid, limp_contract_agent.search(cr, uid ,[('contract_id','=',ids)]))
            partner = self.pool.get('res.partner').browse(cr, uid, part)
            for partner_agent in partner.commission_ids:
                vals={
                    'agent_id':partner_agent.agent_id.id,
                    'commission_id':partner_agent.commission_id.id,
                    'invoice_settle': partner_agent.invoice_settle
                }
                if ids:
                    for id in ids:
                        vals['contract_id']=id
                contract_agent_id=limp_contract_agent.create(cr, uid, vals)
                contract_agent_ids.append(int(contract_agent_id))
            res['value']['contract_agent_ids'] =  contract_agent_ids
        return res

limp_contract()
