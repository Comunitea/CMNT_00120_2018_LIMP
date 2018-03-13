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
from odoo import models, fields, api


class WasteService(models.Model):

    _name = "waste.service"
    _description = "Waste services"
    _inherits = {'account.analytic.account': 'analytic_acc_id'}

    analytic_acc_id = fields.Many2one('account.analytic.account', 'Analytic account', readonly=True, required=True, ondelete="cascade")
    active = fields.Boolean('Active', default=True)
    fiscal_position = fields.Many2one('account.fiscal.position', 'Fiscal position')
    payment_term = fields.Many2one('account.payment.term', 'Payment term')
    payment_mode = fields.Many2one('account.payment.mode', 'Payment type')
    partner_bank_id = fields.Many2one('res.partner.bank', 'Bank account')
    partner_shipping_id = fields.Many2one('res.partner', 'Service address')
    service_picking_ids = fields.One2many('stock.service.picking','service_id','Stock Service Picking')
    name = fields.Char(default='SEQ')
    user_id = fields.Many2one('res.users', 'User', default=lambda r: r.env.user.id)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('waste.service')
        return super(WasteService, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.address_invoice_id = False
            self.partner_shipping_id = False
            self.contact_id = False

        addr = part.address_get(['invoice', 'contact'])

        if addr:
            self.address_invoice_id = addr['invoice']
            self.partner_shipping_id = addr['contact']
            self.contact_id = addr['contact']
