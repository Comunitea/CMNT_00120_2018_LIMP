# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos All Rights Reserved
#    $Omar Castiñeira Saavedra$ <marta@pexego.es>
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

class service_picking_agent(osv.osv):
    _name = 'service.picking.agent'
    _columns = {
        'picking_id':fields.many2one('stock.service.picking', 'Picking', required=False, ondelete='cascade', help=''),
        'partner_id': fields.related('picking_id', 'partner_id', type='many2one', relation='res.partner', string="Customer", readonly=True),
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

service_picking_agent()

class stock_service_picking(osv.osv):

    _inherit = "stock.service.picking"

    _columns = {
        'picking_agent_ids':fields.one2many('service.picking.agent', 'picking_id', 'Agents', states={'draft': [('readonly', False)]})
    }


    def onchange_partner_id(self, cr, uid, ids, part, service_id):
        """manage on_change event in partner_id field"""
        if not part:
            return {'value': {'address_id': False, 'address_invoice_id': False, 'orig_address_id': False}}

        res = super(stock_service_picking, self).onchange_partner_id(cr, uid, ids, part, service_id)

        part = self.pool.get('res.partner').browse(cr, uid, part)
        picking_agent_ids=[]

        service_picking_agent = self.pool.get('service.picking.agent')
        if ids:
            service_picking_agent.unlink(cr, uid, service_picking_agent.search(cr, uid ,[('picking_id','=',ids)]))

        for partner_agent in part.commission_ids:
            vals={
                'agent_id':partner_agent.agent_id.id,
                'commission_id':partner_agent.commission_id.id,
                'invoice_settle': partner_agent.invoice_settle
            }
            if ids:
                for id in ids:
                    vals['picking_id']=id
            picking_agent_id=service_picking_agent.create(cr, uid, vals)
            picking_agent_ids.append(int(picking_agent_id))
        res['value']['picking_agent_ids'] = picking_agent_ids

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        res = super(stock_service_picking, self).create(cr, uid, vals)

        if 'picking_agent_ids' in vals:
            for picking_agent in vals['picking_agent_ids']:
                self.pool.get('service.picking.agent').write(cr, uid, picking_agent[1], {'picking_id':res})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        for picking in self.browse(cr, uid, ids):
            if 'picking_agent_ids' in vals:
                for picking_agent in vals['picking_agent_ids']:
                    if picking_agent[2]:
                        picking_agent[2]['picking_id']=picking.id
                    else:
                        self.pool.get('service.picking.agent').unlink(cr, uid, picking_agent[1])

        return super(stock_service_picking, self).write(cr, uid, ids, vals)

stock_service_picking()

class service_order_toinvoice(osv.osv_memory):

    _inherit = "service.order.toinvoice"

    def create_invoice(self, cr, uid, ids, context=None):
        res = super(service_order_toinvoice, self).create_invoice(cr, uid, ids, context=context)

        for invoice in self.pool.get('account.invoice').browse(cr, uid, res.values()):
            for invoice_line in invoice.invoice_line:
                if invoice_line.service_picking_id and invoice_line.service_picking_id.picking_agent_ids:
                    for sp_agent_id in invoice_line.service_picking_id.picking_agent_ids:
                        vals = {
                                'invoice_line_id': invoice_line.id,
                                'agent_id': sp_agent_id.agent_id.id,
                                'commission_id': sp_agent_id.commission_id.id,
                                'settled': False
                            }

                        line_agent_id=self.pool.get('invoice.line.agent').create(cr, uid, vals)
                        self.pool.get('invoice.line.agent').calculate_commission(cr, uid, [line_agent_id])

        return res

service_order_toinvoice()

class add_to_invoice(osv.osv_memory):

    _inherit = "add.to.invoice"

    def add_to_invoice(self, cr, uid, ids, context=None):
        res = super(add_to_invoice, self).add_to_invoice(cr, uid, ids, context=context)

        for invoice in self.pool.get('account.invoice').browse(cr, uid, res):
            for invoice_line in invoice.invoice_line:
                if invoice_line.service_picking_id and invoice_line.service_picking_id.id in context.get('active_ids', []) and invoice_line.service_picking_id.picking_agent_ids:
                    for sp_agent_id in invoice_line.service_picking_id.picking_agent_ids:
                        vals = {
                                'invoice_line_id': invoice_line.id,
                                'agent_id': sp_agent_id.agent_id.id,
                                'commission_id': sp_agent_id.commission_id.id,
                                'settled': False
                            }

                        line_agent_id=self.pool.get('invoice.line.agent').create(cr, uid, vals)
                        self.pool.get('invoice.line.agent').calculate_commission(cr, uid, [line_agent_id])

        return res

add_to_invoice()
