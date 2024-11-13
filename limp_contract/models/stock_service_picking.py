##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    contract_id = fields.Many2one("limp.contract", "Contract")
    workcenter = fields.Char("Workcenter")

    has_extinguisher_revision = fields.Boolean('Has extinguisher revision')
    extinguisher_revision_ids = fields.One2many(
        'extinguisher.revision',
        'stock_service_picking_id',
        'Extinguisher revision'
    )

    has_bie_revision = fields.Boolean('Has BIE revision')
    bie_revision_ids = fields.One2many(
        'bie.revision',
        'stock_service_picking_id',
        'Extinguisher revision'
    )

    @api.onchange('has_extinguisher_revision')
    def _onchange_has_extinguisher_revision(self):
        self.ensure_one()
        if not self.has_extinguisher_revision:
            self.extinguisher_revision_ids = [(5,)]
        else:
            values = []
            for extinguisher in self.contract_id.extinguisher_and_signal_ids:
                values.append((0, 0, {'extinguisher_and_signal_id': extinguisher.id}))

            self.extinguisher_revision_ids = values

    @api.onchange('has_bie_revision')
    def _onchange_has_bie_revision(self):
        self.ensure_one()
        if not self.has_bie_revision:
            self.bie_revision_ids = [(5,)]
        else:
            values = []
            for bie in self.contract_id.bie_and_signal_ids:
                values.append((0, 0, {'bie_and_signal_id': bie.id}))

            self.bie_revision_ids = values

    @api.model
    def create(self, vals):
        if vals.get("contract_id", False):
            contract = self.env["limp.contract"].browse(vals["contract_id"])
            if not vals.get("delegation_id", False):
                vals["delegation_id"] = contract.delegation_id.id
            if not vals.get("department_id", False):
                vals["department_id"] = contract.department_id.id
            if not vals.get("company_id", False):
                vals["company_id"] = contract.company_id.id
            if not vals.get("parent_id", False):
                vals["parent_id"] = contract.analytic_account_id.id
        return super(StockServicePicking, self).create(vals)

    @api.onchange("contract_id")
    def onchange_contract_id(self):
        if self.contract_id:
            contract = self.contract_id
            self.parent_id = contract.analytic_account_id
            self.department_id = contract.department_id
            self.delegation_id = contract.delegation_id
            self.partner_id = contract.partner_id
            self.manager_id = contract.manager_id
            self.address_invoice_id = contract.address_invoice_id
            self.address_id = contract.address_id
            self.ccc_account_id = contract.bank_account_id
            self.payment_type = contract.payment_type_id
            self.payment_term = contract.payment_term_id
            self.privacy = contract.privacy
            self.address_tramit_id = contract.address_tramit_id
            self.type_ddd_ids = [(6, 0, contract.type_ddd_ids.ids)]
            self.parent_id = contract.analytic_account_id.id
            self.used_product_ids = [(6, 0, contract.used_product_ids.ids)]
