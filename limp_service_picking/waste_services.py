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

class waste_service(osv.osv):

    _name = "waste.service"
    _description = "Waste services"
    _inherits = {'account.analytic.account': 'analytic_acc_id'}

    _columns = {
        'analytic_acc_id': fields.many2one('account.analytic.account', 'Analytic account', readonly=True, required=True, ondelete="cascade"),
        'active': fields.boolean('Active'),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal position'),
        'payment_term': fields.many2one('account.payment.term', 'Payment term'),
        'payment_type': fields.many2one('payment.type', 'Payment type'),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank account'),
        'partner_shipping_id': fields.many2one('res.partner', 'Service address'),
        'service_picking_ids': fields.one2many('stock.service.picking','service_id','Stock Service Picking',)
        }

    _defaults = {
        'active': True,
        'state': 'open',
        'name': 'SEQ'
    }

    def create(self, cr, uid, vals, context=None):
        """Fills waste service seq"""
        if context is None: context = {}
        seq = self.pool.get('ir.sequence').get(cr, uid, 'waste.service')
        vals['name'] = seq

        return super(waste_service, self).create(cr, uid, vals)

    def onchange_partner_id(self, cr, uid, ids, part):
        """manage on_change event in partner_id field"""
        if not part:
            return {'value': {'address_invoice_id': False,
                              'partner_shipping_id': False,
                              'contact_id': False}}

        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['invoice', 'contact'])
        part = self.pool.get('res.partner').browse(cr, uid, part)

        if addr:
            val = {
                'address_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['contact'],
                'contact_id': addr['contact']
            }

            return {'value': val}
        return {}

waste_service()
