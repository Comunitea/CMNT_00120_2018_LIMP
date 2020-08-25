##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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
from odoo import models, fields


class LimpContract(models.Model):

    _inherit = "limp.contract"

    sale_id = fields.Many2one("sale.order", "Sale", readonly=True)

    def action_view_waste_lines(self):
        action = super(LimpContract, self).action_view_waste_lines()
        action["context"] = str(
            {
                "default_picking_type": "wastes",
                "type": "wastes",
                "form_view_ref":
                "limp_service_picking.stock_service_picking_form",
                "default_delegation_id": self.delegation_id.id,
                "default_partner_id": self.partner_id.id,
                "default_manager_id": self.manager_id.id,
                "default_address_invoice_id": self.address_invoice_id.id,
                "default_address_id": self.address_id.id,
                "default_ccc_account_id": self.bank_account_id.id,
                "default_payment_type": self.payment_type_id.id,
                "default_payment_term": self.payment_term_id.id,
                "default_privacy": self.privacy,
                "default_contract_id": self.id,
                "default_sale_id": self.sale_id.id,
            }
        )
        return action

    def action_view_sporadic_service_picking(self):
        action = super(
            LimpContract, self
        ).action_view_sporadic_service_picking()
        action["context"] = str(
            {
                "default_picking_type": "sporadic",
                "type": "sporadic",
                "form_view_ref":
                "limp_service_picking.stock_service_picking_form",
                "default_delegation_id": self.delegation_id.id,
                "default_partner_id": self.partner_id.id,
                "default_manager_id": self.manager_id.id,
                "default_address_invoice_id": self.address_invoice_id.id,
                "default_address_id": self.address_id.id,
                "default_ccc_account_id": self.bank_account_id.id,
                "default_payment_type": self.payment_type_id.id,
                "default_payment_term": self.payment_term_id.id,
                "default_privacy": self.privacy,
                "default_contract_id": self.id,
                "default_sale_id": self.sale_id.id,
            }
        )
        return action
