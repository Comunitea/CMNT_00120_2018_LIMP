# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import models, api, fields


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res.remove('vat')
        return res

    @api.multi
    def open_contract_employees(self):
        self.ensure_one()
        form_view_id = self.env.ref('limp_contract.limp_contract_form')
        tree_view_id = self.env.ref('limp_contract.limp_contract_tree')

        return {
            'name': 'Contracts',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'limp.contract',
            'domain': "[('partner_id', '=', [%s])]" %
                      self.id,
            'context': "{'default_worker': True}",
            'view_id': tree_view_id.id,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'type': 'ir.actions.act_window',
            'nodestroy': True}

    @api.multi
    def open_contract_waste(self):
        self.ensure_one()
        form_view_id = self.env.ref('limp_service_picking.stock_service_picking_form')
        tree_view_id = self.env.ref('limp_service_picking.stock_service_picking_tree')

        return {
            'name': 'Waste',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.service.picking',
            'domain': "[('partner_id', '=', [%s])]" %
                      self.id,
            'context': "{'default_worker': True}",
            'view_id': tree_view_id.id,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'type': 'ir.actions.act_window',
            'nodestroy': True}

    @api.multi
    def open_contract_sporadic(self):
        self.ensure_one()
        form_view_id = self.env.ref('limp_service_picking.stock_sporadic_service_picking_form')
        tree_view_id = self.env.ref('limp_service_picking.stock_sporadic_service_picking_tree')

        return {
            'name': 'Sporadic',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.service.picking',
            'domain': "[('partner_id', '=', [%s])]" %
                      self.id,
            'context': "{'default_worker': True}",
            'view_id': tree_view_id.id,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'type': 'ir.actions.act_window',
            'nodestroy': True}
