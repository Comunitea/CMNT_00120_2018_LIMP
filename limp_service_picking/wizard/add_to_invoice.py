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
from odoo import models, fields, _
from odoo.exceptions import UserError


class AddToInvoice(models.TransientModel):

    _name = "add.to.invoice"

    invoice_id = fields.Many2one("account.invoice", "Invoice", required=False)

    def view_init(self, fields_list):
        res = super(AddToInvoice, self).view_init(fields_list)
        for pick in self.env["stock.service.picking"].browse(
            self._context.get("active_ids", [])
        ):
            if (
                pick.state != "closed"
                or pick.invoice_line_ids
                or pick.invoice_type == "noinvoice"
            ):
                raise UserError(
                    _(
                        "The service order %s does not prepares to be invoiced or it was already invoiced."
                    )
                    % (pick.name)
                )
        return res

    def open_invoice(self):
        invoice_ids = []
        invoice_ids = self.add_to_invoice()
        if not invoice_ids:
            raise UserError(_("No Invoices were created"))
        action = self.env.ref("account.action_invoice_tree1").read()[0]
        action["domain"] = (
            "[('id','in', [" + ",".join(map(str, invoice_ids)) + "])]"
        )
        return action

    def add_to_invoice(self):
        for service_picking in self.env["stock.service.picking"].browse(
            self._context.get("active_ids", [])
        ):
            comment = False
            partner = service_picking.partner_id
            fpos = partner.property_account_position_id
            invoice_vals = {
                "name": (self.invoice_id.name or u"")
                + u", "
                + (service_picking.name or u""),
                "origin": (self.invoice_id.origin or "")
                + u", "
                + (service_picking.name or u""),
                "comment": (
                    comment
                    and (
                        self.invoice_id.comment
                        and self.invoice_id.comment + u"\n" + comment
                        or comment
                    )
                )
                or (
                    self.invoice_id.comment and self.invoice_id.comment or u""
                ),
            }
            self.invoice_id.write(invoice_vals)

            for move_line in service_picking.service_invoice_concept_ids:
                name = (service_picking.name or u"") + u"-" + move_line.name
                account_id = (
                    move_line.product_id.product_tmpl_id.property_account_income_id
                )
                if not account_id:
                    account_id = (
                        move_line.product_id.categ_id.property_account_income_categ_id
                    )
                if not account_id:
                    raise UserError(
                        _("Income account in product %s is not set")
                        % move_line.product_id.name
                    )

                price_unit = move_line.price
                tax_ids = fpos.map_tax(move_line.product_id.taxes_id)._ids

                account_id = fpos.map_account(account_id).id
                invoice_line_id = self.env["account.invoice.line"].create(
                    {
                        "name": name,
                        "invoice_id": self.invoice_id.id,
                        "product_id": move_line.product_id.id,
                        "uom_id": move_line.product_uom
                        and move_line.product_uom.id
                        or move_line.product_id.uom_id.id,
                        "account_id": account_id,
                        "price_unit": price_unit,
                        "quantity": move_line.product_qty,
                        "invoice_line_tax_ids": [(6, 0, tax_ids)],
                        "building_site_id": service_picking.building_site_id
                        and service_picking.building_site_id.id
                        or False,
                        "account_analytic_id": service_picking.analytic_acc_id.id,
                        "service_picking_id": service_picking.id,
                    }
                )
            service_picking.write({"invoice_type": "invoiced"})

            if service_picking.taxes:
                if not service_picking.product_tax_id:
                    raise UserError(
                        _("Product tax is not set in picking %s")
                        % service_picking.name
                    )

                account_id = (
                    service_picking.product_tax_id.product_tmpl_id.property_account_income_id
                )
                if not account_id:
                    account_id = (
                        service_picking.product_tax_id.categ_id.property_account_income_categ_id
                    )
                if not account_id:
                    raise UserError(
                        _("Income account in product %s is not set")
                        % service_picking.product_tax_id.name
                    )

                tax_ids = fpos.map_tax(
                    service_picking.product_tax_id.taxes_id
                )._ids

                self.env["account.invoice.line"].create(
                    {
                        "name": service_picking.product_tax_id.name,
                        "invoice_id": self.invoice_id.id,
                        "product_id": service_picking.product_tax_id.id,
                        "uom_id": service_picking.product_tax_id.uom_id.id,
                        "account_id": fpos.map_account(account_id).id,
                        "price_unit": service_picking.taxes,
                        "quantity": 1.0,
                        "invoice_line_tax_ids": [(6, 0, tax_ids)],
                        "building_site_id": service_picking.building_site_id
                        and service_picking.building_site_id.id
                        or False,
                        "account_analytic_id": service_picking.analytic_acc_id.id,
                        "service_picking_id": service_picking.id,
                    }
                )

            if service_picking.sand_amount:
                if not service_picking.product_sand_id:
                    raise UserError(
                        _("Product sand treatment is not set in picking %s")
                        % service_picking.name
                    )

                account_id = (
                    service_picking.product_sand_id.product_tmpl_id.property_account_income_id
                )
                if not account_id:
                    account_id = (
                        service_picking.product_sand_id.categ_id.property_account_income_categ_id
                    )
                if not account_id:
                    raise UserError(
                        _("Income account in product %s is not set")
                        % service_picking.product_sand_id.name
                    )

                tax_ids = fpos.map_tax(
                    service_picking.product_sand_id.taxes_id
                )._ids

                self.env["account.invoice.line"].create(
                    {
                        "name": service_picking.product_sand_id.name,
                        "invoice_id": self.invoice_id.id,
                        "product_id": service_picking.product_sand_id.id,
                        "uom_id": service_picking.product_sand_id.uom_id.id,
                        "account_id": fpos.map_account(account_id).id,
                        "price_unit": service_picking.sand_amount,
                        "quantity": 1.0,
                        "invoice_line_tax_ids": [(6, 0, tax_ids)],
                        "building_site_id": service_picking.building_site_id
                        and service_picking.building_site_id.id
                        or False,
                        "account_analytic_id": service_picking.analytic_acc_id.id,
                        "service_picking_id": service_picking.id,
                    }
                )

            self.invoice_id.compute_taxes()

        return [self.invoice_id.id]
