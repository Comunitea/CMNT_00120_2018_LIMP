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

from odoo import models, api


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.multi
    def open_contract_employees(self):
        self.ensure_one()
        form_view_id = self.env.ref("limp_contract.limp_contract_form")
        tree_view_id = self.env.ref("limp_contract.limp_contract_tree")

        return {
            "name": "Contracts",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "limp.contract",
            "domain": "[('partner_id', 'child_of', [%s])]" % self.id,
            "context": "{'default_partner_id': %s}" % self.id,
            "view_id": tree_view_id.id,
            "views": [(tree_view_id.id, "tree"), (form_view_id.id, "form")],
            "type": "ir.actions.act_window",
            "nodestroy": True,
        }

    @api.multi
    def open_contract_waste(self):
        self.ensure_one()
        form_view_id = self.env.ref(
            "limp_service_picking.stock_service_picking_form"
        )
        tree_view_id = self.env.ref(
            "limp_service_picking.stock_service_picking_tree"
        )

        return {
            "name": "Waste",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "stock.service.picking",
            "domain": "[('picking_type','=','wastes'),"
                      "('partner_id', 'child_of', [%s])]" % self.id,
            "context":
            "{'default_partner_id': %s, 'type': 'wastes'}" % self.id,
            "view_id": tree_view_id.id,
            "views": [(tree_view_id.id, "tree"), (form_view_id.id, "form")],
            "type": "ir.actions.act_window",
            "nodestroy": True,
        }

    @api.multi
    def open_contract_sporadic(self):
        self.ensure_one()
        form_view_id = self.env.ref(
            "limp_service_picking.stock_sporadic_service_picking_form"
        )
        tree_view_id = self.env.ref(
            "limp_service_picking.stock_sporadic_service_picking_tree"
        )

        return {
            "name": "Sporadic",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "stock.service.picking",
            "domain": "[('picking_type','=','sporadic'),"
                      "('partner_id', 'child_of', [%s])]" % self.id,
            "context":
            "{'default_partner_id': %s, 'type': 'sporadic'}" % self.id,
            "view_id": tree_view_id.id,
            "views": [(tree_view_id.id, "tree"), (form_view_id.id, "form")],
            "type": "ir.actions.act_window",
            "nodestroy": True,
        }

    @api.depends('street')
    def _compute_display_name(self):
        super()._compute_display_name()

    def _get_name(self):
        partner = self
        name = partner.name or ''

        if partner.company_name or partner.parent_id:
            if not partner.is_company:
                name = self._get_contact_name(partner, name or partner.street)
        else:
            return super()._get_name()

        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name
