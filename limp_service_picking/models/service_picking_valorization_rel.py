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
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ServicePickingValorizationRel(models.Model):
    _name = "service.picking.valorization.rel"

    product_id = fields.Many2one("product.product", "Product", required=True)
    name = fields.Char("Name", size=128, required=True)
    product_qty = fields.Float(
        "Qty.", digits=dp.get_precision("Sale Price"), required=True
    )
    product_uom_id = fields.Many2one("uom.uom", "UoM", readonly=True,
                                     related="product_id.uom_id")
    service_picking_id = fields.Many2one(
        "stock.service.picking", "Service picking"
    )
    billable = fields.Boolean("Billable")
    memory_include = fields.Boolean("Memory include")
    gross_weight = fields.Float(
        "Gross (T.)", digits=(12, 5), help="Gross weight in T"
    )
    tare = fields.Float("Tare (T.)", digits=(12, 5), help="Tare in T.")
    net_weight = fields.Float(
        "Net (T.)", digits=(12, 5), help="Net weight in T."
    )
    overload_qty = fields.Float(
        "Overload", digits=(12, 2), help="Overload in m³"
    )
    volume = fields.Float("Volume (m³)", digits=(12, 2), help="Volume in m³")
    ler_code = fields.Char("Ler", size=20)
    no_compute = fields.Boolean("No compute")
    delegation_id = fields.Many2one(
        "hr.department", "Department", change_default=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        change_default=True,
        default=lambda r: r._context.get(
            "company_id", r.env.user.company_id.id
        ),
    )

    @api.onchange("product_id")
    def onchange_product_id_warning(self):
        if not self.product_id:
            return

        self.name = self.product_id.name
        if self.product_id.ler_code_id:
            self.ler_code = self.product_id.ler_code_id.code

        if self.service_picking_id.manager_partner_id:
            partner_ids = (
                self.env["res.company"].sudo().search([]).mapped("partner_id")
            )
            partner_ids |= partner_ids.mapped('child_ids')
            if self.service_picking_id.manager_partner_id not in partner_ids:
                self.memory_include = False
            else:
                self.memory_include = True

        if self.product_id.picking_warn != "no-message":
            warning = {}
            title = _("Warning for %s") % self.product_id.name
            message = self.product_id.picking_warn_msg
            warning["title"] = title
            warning["message"] = message
            if self.product_id.picking_warn == "block":
                self.product_id = False
            return {"warning": warning}

    @api.onchange("net_weight")
    def onchange_net_weight(self):
        if self.no_compute or not self.product_id:
            return

        if self.product_id.ler_code_id and self.product_id.ler_code_id.density:
            self.product_qty = round(
                self.net_weight / self.product_id.ler_code_id.density, 2
            )
            self.volume = round(
                self.net_weight / self.product_id.ler_code_id.density, 2
            )

    @api.onchange("product_qty")
    def onchange_product_qty(self):
        if self.no_compute or not self.product_id:
            return
        self.volume = self.product_qty
        if self.product_id.ler_code_id and self.product_id.ler_code_id.density:
            self.net_weight = round(
                self.product_qty * self.product_id.ler_code_id.density, 2
            )

    @api.onchange("volume")
    def onchange_volume(self):
        if self.no_compute or not self.product_id:
            return
        self.product_qty = self.volume
        if self.product_id.ler_code_id and self.product_id.ler_code_id.density:
            self.net_weight = round(
                self.volume * self.product_id.ler_code_id.density, 2
            )

    @api.model
    def create(self, vals):
        if vals.get("memory_include", False):
            if not self.env.user.has_group(
                "limp_service_picking.group_waste_memory"
            ):
                vals["memory_include"] = False
        return super(ServicePickingValorizationRel, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get("memory_include", False):
            if not self.env.user.has_group(
                "limp_service_picking.group_waste_memory"
            ):
                vals["memory_include"] = False
        return super(ServicePickingValorizationRel, self).write(vals)
