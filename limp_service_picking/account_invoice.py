# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from osv import osv, fields

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'building_site_id': fields.many2one('building.site.services', 'Building Site'),
        'service_picking_id': fields.many2one('stock.service.picking', 'Service picking', readonly=True),
        'move_id': fields.many2one('stock.move', 'Move'),
        'quantity': fields.float('Quantity', digits=(12,3), required=True),
    }
account_invoice_line()

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'intercompany': fields.boolean('Intercompany', readonly=True),
        'intercompany_invoice_id': fields.many2one('account.invoice', 'Intercompany invoice', readonly=True)
    }

    def _refund_cleanup_lines(self, cr, uid, lines):
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        for line in res:
            line[2]['building_site_id'] = line[2].get('building_site_id', False) and line[2]['building_site_id'][0]
            line[2]['service_picking_id'] = line[2].get('service_picking_id', False) and line[2]['service_picking_id'][0]

        return res

account_invoice()

class stock_service_picking(osv.osv):

    _inherit = 'stock.service.picking'

    _columns = {
        'invoice_line_ids': fields.one2many('account.invoice.line', 'service_picking_id', 'Invoice lines', readonly=True),
        'invoice_id': fields.related('invoice_line_ids', 'invoice_id', type="many2one", relation="account.invoice", string="Invoice", readonly=True)
    }

stock_service_picking()

class account_journal(osv.osv):

    _inherit = "account.journal"

    _columns = {
        'intercompany': fields.boolean('Intercompany'),
    }

account_journal()
