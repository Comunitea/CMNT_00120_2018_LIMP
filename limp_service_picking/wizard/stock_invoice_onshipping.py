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


class StockInvoiceOnshipping(models.TransientModel):

    _name = "wizard.stock.invoice.onshipping"
    _description = "Stock Invoice Onshipping"

    @api.model
    def _get_default_journal(self):
        browse_picking = self.env['stock.picking'].\
            browse(self._context.get('active_ids', []))
        journal_id = False
        if browse_picking:
            pick = browse_picking[0]
            if pick.from_spicking and pick.picking_type_id.code == 'incoming':
                journal_type = 'sale'
            elif pick.invoice_type == 'out_invoice':
                journal_type = 'sale'
            elif pick.invoice_type == 'in_invoice':
                journal_type = 'purchase'
            else:
                journal_type = 'sale'

            journal_id = self.env['account.journal'].\
                search([('type', '=', journal_type)], limit=1)

        return journal_id

    @api.model
    def _get_journal_type(self):
        res_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(res_ids)
        pick = pickings and pickings[0]
        type = pick.invoice_type
        if not pick or not pick.move_lines or \
                (pick.from_spicking and
                 pick.picking_type_id.code == 'incoming'):
            return 'sale'
        return 'purchase' if type == 'in_invoice' else 'sale'

    journal_id = fields.Many2one("account.journal", 'Destination Journal',
                                 required=True, default=_get_default_journal)
    journal_type = fields.Selection([('purchase', 'Create Supplier Invoice'),
                                     ('sale', 'Create Customer Invoice')],
                                    'Journal Type', readonly=True,
                                    default=_get_journal_type)
    group = fields.Boolean("Group by partner")
    invoice_date = fields.Date('Invoice Date')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        domain = {}
        if self.journal_id:
            self.journal_type = self.journal_id.type
            domain['journal_id'] = [('type', '=', self.journal_id.type)]
        elif self._context.get('active_ids'):
            type = self._get_journal_type()
            self.journal_type = type
            domain['journal_id'] = [('type', '=', type)]

        return {'domain': domain}

    def view_init(self, fields_list):
        res = super(StockInvoiceOnshipping, self).view_init(fields_list)
        count = 0
        active_ids = self._context.get('active_ids', [])
        for pick in self.env['stock.picking'].browse(active_ids):
            if pick.invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == count:
            raise UserError(_('None of these picking lists require invoicing'))
        return res

    def open_invoice(self):
        invoices = self.create_invoice()
        if not invoices:
            raise UserError(_('No invoice created!'))

        action = {}
        if 'out' in invoices[0].type:
            action = self.env.ref('account.action_invoice_tree1')
        elif 'in' in invoices[0].type:
            action = self.env.ref('account.action_invoice_tree2')

        if action:
            action = action.read()[0]
            action['domain'] = \
                "[('id','in', ["+','.join(map(str, invoices.ids))+"])]"
            return action
        return True

    def create_invoice(self):
        self.ensure_one()
        pickings = self.env['stock.picking'].\
            browse(self._context.get('active_ids', False))
        res = pickings.action_invoice_create(
            journal_id=self.journal_id.id,
            group=self.group,
            date=self.invoice_date)
        return res
