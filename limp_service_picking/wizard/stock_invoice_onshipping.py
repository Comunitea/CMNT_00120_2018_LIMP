# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, api, _
from odoo.exceptions import UserError

JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],
}


class StockInvoiceOnshipping(models.TransientModel):

    _name = "stock.invoice.onshipping"
    _description = "Stock Invoice Onshipping"

    def _get_journal_id(self):
        journal_obj = self.env['account.journal']
        vals = []

        value = journal_obj.search([('type', 'in', ['purchase_refund','sale','purchase','sale_refund'])])
        for jr_type in value:
            t1 = jr_type.id, jr_type.name
            vals.append(t1)
        return vals

    def _get_default_journal(self):
        vals = []
        browse_picking = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        journal_id = False

        for pick in browse_picking:
            src_usage = pick.move_lines[0].location_id.usage
            dest_usage = pick.move_lines[0].location_dest_id.usage
            type = pick.picking_type_id.code
            if pick.from_spicking and type == 'incoming':
                journal_type = 'sale'
            elif type == 'outgoing' and dest_usage == 'supplier':
                journal_type = 'purchase_refund'
            elif type == 'outgoing' and dest_usage == 'customer':
                journal_type = 'sale'
            elif type == 'incoming' and src_usage == 'supplier':
                journal_type = 'purchase'
            elif type == 'incoming' and src_usage == 'customer':
                journal_type = 'sale_refund'
            else:
                journal_type = 'sale'

            journal_id = self.env['account.journal'].search([('type', '=',journal_type)])._ids

        return journal_id

    def _get_journal_type(self):
        res_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(res_ids)
        pick = pickings and pickings[0]
        if not pick or not pick.move_lines:
            return 'sale'
        type = pick.picking_type_id.code
        usage = pick.move_lines[0].location_id.usage if type == 'incoming' else pick.move_lines[0].location_dest_id.usage
        return JOURNAL_TYPE_MAP.get((type, usage), ['sale'])[0]

    journal_id = fields.Selection(_get_journal_id, 'Destination Journal', required=True, default=_get_default_journal)
    journal_type = fields.Selection([('purchase_refund', 'Refund Purchase'), ('purchase', 'Create Supplier Invoice'),
                                      ('sale_refund', 'Refund Sale'), ('sale', 'Create Customer Invoice')], 'Journal Type', readonly=True, default=_get_journal_type)
    group = fields.Boolean("Group by partner")
    invoice_date = fields.Date('Invoice Date')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        domain = {}
        active_id = self._context.get('active_id')
        if active_id:
            picking = self.env['stock.picking'].browse(active_id)
            type = picking.picking_type_id.code
            usage = picking.move_lines[0].location_id.usage if type == 'incoming' else picking.move_lines[0].location_dest_id.usage
            journal_types = JOURNAL_TYPE_MAP.get((type, usage), ['sale', 'purchase', 'sale_refund', 'purchase_refund'])
            domain['journal_id'] = [('type', 'in', journal_types)]
        if self.journal_id:
            journal = self.env['account.journal'].browse(self.journal_id)
            self.journal_type = journal.type
        return {'domain': domain}

    def view_init(self, fields_list):
        res = super(StockInvoiceOnshipping, self).view_init(fields_list)
        count = 0
        active_ids = self._context.get('active_ids',[])
        for pick in self.env['stock.picking'].browse(active_ids):
            if pick.invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == count:
            raise UserError(_('None of these picking lists require invoicing.'))
        return res

    def open_invoice(self):
        invoice_ids = self.create_invoice()
        if not invoice_ids:
            raise UserError(_('No invoice created!'))

        action_model = False
        action = {}

        journal2type = {'sale':'out_invoice', 'purchase':'in_invoice', 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
        inv_type = journal2type.get(self.journal_type) or 'out_invoice'
        data_pool = self.pool.get('ir.model.data')
        if 'out' in inv_type:
            action = self.env.ref('account.action_invoice_tree1')
        elif 'in' in inv_type:
            action = self.env.ref('account.action_invoice_tree2')


        if action:
            action = action.read()[0]
            action['domain'] = "[('id','in', ["+','.join(map(str, invoice_ids))+"])]"
            return action
        return True

    def create_invoice(self):
        picking_pool = self.pool.get('stock.picking')
        journal2type = {'sale':'out_invoice', 'purchase':'in_invoice', 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
        inv_type = journal2type.get(self.journal_type) or 'out_invoice'

        pickings = self.env['stock.picking'].browse(self._context.get('active_ids', False))
        res = pickings.action_invoice_create(
              journal_id = self.journal_id,
              group = self.group,
              type = inv_type,
              date=self.invoice_date)
        return res
