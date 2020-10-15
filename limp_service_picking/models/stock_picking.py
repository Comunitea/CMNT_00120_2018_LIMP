##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, _, api, exceptions
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.onchange('product_uom_qty', 'product_uom')
    def onchange_product_uom_qty(self):
        if self.product_id.stock_secondary_uom_id:
            uom = self.product_uom
            factor = self.product_id.stock_secondary_uom_id.factor * uom.factor
            move_line_qty = self.product_uom_qty
            qty = float_round(
                move_line_qty / (factor or 1.0),
                precision_rounding=self.product_id.
                stock_secondary_uom_id.uom_id.rounding
            )
            self.secondary_uom_qty = qty
            self.secondary_uom_id = self.product_id.stock_secondary_uom_id.id

    @api.multi
    def force_set_qty_done(self, reset=False, field='product_uom_qty'):
        visited_products = []
        user = self.env.user
        reserve_moves1 = self.env["stock.move"]
        reserve_moves2 = self.env["stock.move"]
        for move in self.\
                filtered(lambda x: x.state in ('confirmed', 'assigned',
                                               'partially_available')):
            pick = move.picking_id
            if move.product_id.ler_code_id and \
                    pick.picking_type_id.code == "outgoing":
                orig_qty = move.product_id.with_context(
                    location=move.location_id.id
                ).virtual_available
                if (
                    orig_qty < 0.0
                    and move.product_id.id not in visited_products
                ):
                    visited_products.append(move.product_id.id)
                    if not user.company_id.reserve_product_id:
                        raise UserError(
                            _("You have not enough quantity to serve the "
                              "product %s. Then you have to set the reserve "
                              "product in company for using it.")
                            % (move.product_id.name,)
                        )
                    else:
                        reserve_product_id = (
                            user.company_id.reserve_product_id
                        )
                        if (
                            reserve_product_id.uom_id.category_id.id
                            == move.product_id.uom_id.category_id.id
                        ):
                            qty = move.product_id.uom_id._compute_quantity(
                                -(orig_qty),
                                user.company_id.reserve_product_id.uom_id,
                            )
                        else:
                            qty = (
                                -orig_qty
                                / move.product_id.ler_code_id.density
                            )

                        # movimiento de consumo del producto resevado,
                        # de Stock a producción
                        move_vals = {
                            "name": "Used to serve %s in picking %s"
                            % (move.product_id.name, pick.name),
                            "product_id":
                            user.company_id.reserve_product_id.id,
                            "product_uom_qty": qty,
                            "product_uom":
                            user.company_id.reserve_product_id.uom_id.id,
                            "location_id": move.location_id.id,
                            "location_dest_id":
                            user.company_id.reserve_product_id.
                            property_stock_production.id,
                        }
                        reserve_moves1 |= self.env["stock.move"].create(
                            move_vals
                        )
                        # movimiento de creación del producto a enviar
                        move_vals2 = {
                            "name": "Created from reserve product",
                            "product_id": move.product_id.id,
                            "product_uom_qty": -(orig_qty),
                            "product_uom": move.product_id.uom_id.id,
                            "location_id":
                            move.product_id.property_stock_production.id,
                            "location_dest_id": move.location_id.id,
                        }
                        reserve_moves2 |= self.env["stock.move"].create(
                            move_vals2
                        )
            if reserve_moves1:
                pick_type_internal = self.env["stock.picking.type"].search(
                    [
                        ("code", "=", "internal"),
                        "|",
                        (
                            "default_location_src_id",
                            "=",
                            reserve_moves1[0].location_id.id,
                        ),
                        (
                            "default_location_dest_id",
                            "=",
                            reserve_moves1[0].location_id.id,
                        ),
                    ]
                )

                pick_1 = self.env["stock.picking"].create(
                    {
                        "picking_type_id": pick_type_internal.id,
                        "location_id": reserve_moves1[0].location_id.id,
                        "location_dest_id": reserve_moves1[
                            0
                        ].location_dest_id.id,
                        "origin": pick.name,
                    }
                )
                reserve_moves1.write({"picking_id": pick_1.id})
                pick_1.action_confirm()
                pick_1.force_set_qty_done()
                pick_1.action_done()
            if reserve_moves2:
                pick_type_internal = self.env["stock.picking.type"].search(
                    [
                        ("code", "=", "internal"),
                        "|",
                        (
                            "default_location_src_id",
                            "=",
                            reserve_moves2[0].location_dest_id.id,
                        ),
                        (
                            "default_location_dest_id",
                            "=",
                            reserve_moves2[0].location_dest_id.id,
                        ),
                    ]
                )

                pick_2 = self.env["stock.picking"].create(
                    {
                        "picking_type_id": pick_type_internal.id,
                        "location_id": reserve_moves2[0].location_id.id,
                        "location_dest_id": reserve_moves2[
                            0
                        ].location_dest_id.id,
                        "origin": pick.name,
                    }
                )
                reserve_moves2.write({"picking_id": pick_2.id})
                pick_2.action_confirm()
                pick_2.force_set_qty_done()
                pick_2.action_done()

            move.quantity_done = not reset and move[field] or 0.0


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stock_service_picking_id = fields.Many2one(
        "stock.service.picking", "Stock service picking"
    )
    from_spicking = fields.Boolean("From service picking", readonly=True)
    invoice_type = fields.Selection(
        [("out_invoice", "Out invoice"), ("in_invoice", "In invoice")],
        "Invoice type",
    )
    memory_include = fields.Boolean("Include in annual memory")
    waste_or_arid = fields.Selection(
        [("waste", "Wastes"), ("arid", "Arid")], "Waste/Arid", default="waste"
    )
    manager_or_productor = fields.Selection(
        [("manager", "Manager"), ("productor", "Productor")],
        "Manager/Productor",
        default="productor",
    )
    carrier_id = fields.Many2one("res.partner", "Carrier")
    license_plate = fields.Char("License plate", size=18)
    driver_id = fields.Many2one("hr.employee", "Driver")
    delivery_kms = fields.Integer("Delivery kms.")
    arrival_kms = fields.Integer("Arrival kms.")
    delivery_hours = fields.Float("Delivery hours", digits=(4, 2))
    displacement_hours = fields.Float("Displacement hours", digits=(4, 2))
    work_hours = fields.Float("Work hours", digits=(4, 2))
    tranfer_hours = fields.Float("Transfer hours", digits=(4, 2))
    arrival_hours = fields.Float("Arrival hours", digits=(4, 2))
    invoice_state = fields.Selection(
        [
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable"),
        ],
        string="Invoice Control",
        required=True,
        default="none",
    )
    reserved_availability = fields.Float(
        'Quantity Reserved', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    quantity_done = fields.Float(
        'Quantity Done', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    product_uom_qty = fields.Float(
        'Quantity', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    products = fields.Char("Products", compute="_get_pick_products",
                           store=True)

    @api.depends('move_lines')
    def _get_pick_products(self):
        for pick in self:
            pick.products = ", ".\
                join([x.name for x in pick.move_lines.mapped('product_id')])

    @api.multi
    def force_set_qty_done(self):
        field = self._context.get('field', 'product_uom_qty')
        reset = self._context.get('reset', False)
        states = ('confirmed', 'assigned')
        for picking in self:
            picking.action_assign()
            if picking.state not in states:
                raise exceptions.\
                    UserError(_('State {} incorrect for {}'.
                                format(picking.state, picking.name)))
            picking.move_lines.force_set_qty_done(reset, field)

    @api.multi
    def compute_picking_qties(self):
        for pick in self:
            pick.quantity_done = sum(x.quantity_done for x in pick.move_lines)
            pick.reserved_availability = sum(x.reserved_availability
                                             for x in pick.move_lines)
            pick.product_uom_qty = sum(x.product_uom_qty
                                       for x in pick.move_lines)

    def action_invoice_create(self, journal_id, group, date):
        grouped_pickings = {}
        for picking in self:
            if (
                picking.state != "done"
                or picking.invoice_state != "2binvoiced"
            ):
                continue
            type = picking.invoice_type or 'out_invoice'
            if group:
                if picking.partner_id not in grouped_pickings:
                    grouped_pickings[picking.partner_id] = self.env[
                        "stock.picking"
                    ]
                grouped_pickings[picking.partner_id] |= picking
            else:
                grouped_pickings[picking] = picking
        invoices = self.env["account.invoice"]
        for key in grouped_pickings:
            if not group:
                partner = key.partner_id
                origin = key.name
            else:
                partner = key
                origin = ", ".join([x.name for x in grouped_pickings[key]])
            invoice_vals = {
                "partner_id": partner.id,
                "origin": origin,
                "type": type,
                "journal_id": journal_id,
                "date_invoice": date,
                "account_id": False,
                "payment_term_id": False,
                "date_due": False,
                "fiscal_position_id": False,
                "partner_bank_id": False,
            }
            specs = self.env["account.invoice"]._onchange_spec()
            updates = self.env["account.invoice"].onchange(
                invoice_vals, ["partner_id"], specs
            )
            value = updates.get("value", {})
            for name, val in list(value.items()):
                if isinstance(val, tuple):
                    value[name] = val[0]
            invoice_vals.update(value)
            invoice = self.env["account.invoice"].create(invoice_vals)
            for operation in grouped_pickings[key].mapped(
                "move_lines"
            ):
                invoice_line_vals = {
                    "product_id": operation.product_id.id,
                    "quantity": operation.quantity_done,
                    "uom_id": operation.product_uom.id,
                    "price_unit": False,
                    "name": False,
                    "invoice_line_tax_ids": False,
                    "account_id": False,
                    "account_analytic_id": False,
                    "invoice_id": invoice.id,
                }
                specs = self.env["account.invoice.line"]._onchange_spec()
                updates = self.env["account.invoice.line"].onchange(
                    invoice_line_vals, ["product_id"], specs
                )
                value = updates.get("value", {})
                for name, val in list(value.items()):
                    if isinstance(val, tuple):
                        value[name] = val[0]
                invoice_line_vals.update(value)
                self.env["account.invoice.line"].create(invoice_line_vals)
            if not invoice.invoice_line_ids:
                invoice.unlink()
            else:
                invoice.compute_taxes()
                invoices |= invoice
            grouped_pickings[key].write({"invoice_state": "invoiced"})
        return invoices
