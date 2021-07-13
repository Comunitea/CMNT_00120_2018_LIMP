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

"""new model between stock_move and analytic_account"""

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountAnalyticStockMove(models.Model):
    """new model between stock_move and analytic_account"""

    _name = "account.analytic.stock.move"
    _description = "Model between stock_move and analytic_account"
    _rec_name = "move_id"

    @api.model
    def _get_default_employee_id(self):
        employee_id = False
        if self._context.get("employee_id", False):
            employee_id = self._context["employee_id"]
        elif self.env.user.employee_ids:
            employee_id = self.env.user.employee_ids[0].id
        return employee_id

    @api.model
    def _get_default_location_id(self):
        employee = self.env["hr.employee"].browse(
            self._get_default_employee_id()
        )
        return employee.location_id.id

    employee_id = fields.Many2one(
        "hr.employee",
        "Manager",
        required=True,
        states={"second": [("readonly", True)]},
        default=_get_default_employee_id,
    )
    location_id = fields.Many2one(
        "stock.location",
        "Location",
        required=True,
        states={"second": [("readonly", True)]},
        default=_get_default_location_id,
        domain=[("usage", "=", "internal")],
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        required=True,
        states={"second": [("readonly", True)]},
    )
    product_qty = fields.Float(
        "Quantity",
        required=True,
        digits=dp.get_precision("Product UoM"),
        states={"second": [("readonly", True)]},
        default=1.0,
    )
    move_id = fields.Many2one("stock.move", "Move", readonly=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        "Analytic",
        states={"second": [("readonly", True)]},
    )
    state = fields.Selection(
        [("first", "First"), ("second", "Second")],
        "State",
        readonly=True,
        default="first",
    )
    date = fields.Date("Date", required=True, default=fields.Date.today,
                       states={'second': [('readonly', True)]})

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id and self.employee_id.location_id:
            self.location_id = self.employee_id.location_id.id

    @api.model
    def create(self, vals):

        res = super(AccountAnalyticStockMove, self).create(vals)
        user = self.env.user
        if not res.location_id and not res.employee_id.location_id:
            raise UserError(_("Employee must have an associated location !"))
        if (
            not user.company_id.partner_id.property_stock_customer
            or user.company_id.partner_id.property_stock_customer.usage
            != "customer"
        ):
            raise UserError(
                _(
                    "Company must have set an output customer location in its "
                    "partner form !"
                )
            )
        move_vals = {
            "date": res.date,
            "product_id": res.product_id.id,
            "product_uom_qty": abs(res.product_qty),
            "product_uom": res.product_id.uom_id.id,
            "origin": res.analytic_account_id.name,
            "location_id": res.location_id.id,
            "location_dest_id": user.company_id.
            partner_id.property_stock_customer.id,
            "name": res.analytic_account_id.name
            + _(": Out ")
            + res.product_id.name,
            "company_id": user.company_id.id,
            "partner_id": user.company_id.partner_id.id,
        }
        if res.product_qty < 0:
            move_vals['location_id'] = user.company_id.\
                partner_id.property_stock_customer.id
            move_vals['location_dest_id'] = res.location_id.id
            move_vals['name'] = res.analytic_account_id.name + \
                _(": Out ") + res.product_id.name
        move = self.env["stock.move"].create(move_vals)

        move._action_confirm()

        res.write({"move_id": move.id})

        return res

    @api.multi
    def write(self, vals):
        for line in self:
            if (
                vals.get("location_id")
                and vals["location_id"] != line.location_id.id
            ):
                if (vals.get("product_qty") and vals["product_qty"] < 0) or \
                        (not vals.get("product_qty") and line.product_qty < 0):
                    line.move_id.location_dest_id = vals["location_id"]
                else:
                    line.move_id.location_id = vals["location_id"]
            if (
                vals.get("product_id")
                and vals["product_id"] != line.product_id.id
            ):
                line.move_id.product_id = vals["product_id"]
                product = self.env["product.product"].browse(
                    vals["product_id"]
                )
                line.move_id.product_uom = product.uom_id.id
                if (vals.get("product_qty") and vals["product_qty"] < 0) or \
                        (not vals.get("product_qty") and line.product_qty < 0):
                    line.move_id.name = (
                        line.analytic_account_id.name + _(": IN ") +
                        product.name,
                    )
                else:
                    line.move_id.name = (
                        line.analytic_account_id.name + _(": Out ") +
                        product.name,
                    )
            if (
                vals.get("product_qty")
                and vals["product_qty"] != line.product_qty
            ):
                line.move_id.product_uom_qty = abs(vals["product_qty"])
        return super(AccountAnalyticStockMove, self).write(vals)

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        user = self.env.user
        self.move_id._action_assign()
        if self.move_id.state != 'assigned':
            raise UserError(_("No stock available to confirm consumption"))
        for line in self.move_id.move_line_ids:
            line.qty_done = line.product_uom_qty
        self.move_id._action_done()

        material_tag = self.env.ref(
            "analytic_material_costs.material_cost_tag"
        )

        account_id = (
            self.product_id.product_tmpl_id.property_account_expense_id.id
        )
        if not account_id:
            account_id = (
                self.product_id.categ_id.property_account_expense_categ_id.id
            )
            if not account_id:
                raise UserError(
                    _(
                        "No product and product category expense property "
                        "account defined on the related product.\nFill these"
                        " on product form."
                    )
                )

        line_vals = {
            "amount": -(self.product_id.standard_price * self.product_qty),
            "name": self.analytic_account_id.name
            + _(": Out ")
            + self.product_id.name,
            "company_id": user.company_id.id,
            "product_id": self.product_id.id,
            "tag_ids": [(4, material_tag.id)],
            "account_id": self.analytic_account_id.id,
            "general_account_id": account_id,
            "date": self.date,
            'delegation_id': self.analytic_account_id.delegation_id.id,
            'department_id': self.analytic_account_id.department_id.id,
            'manager_id': self.analytic_account_id.manager_id.id
        }
        if self.move_id.location_id.usage != 'internal':
            line_vals['name'] = self.analytic_account_id.name + \
                _(": IN ") + self.product_id.name
        self.env["account.analytic.line"].create(line_vals)
        self.state = "second"

    @api.multi
    def unlink(self):
        """Avoid delete an analytic entry"""
        for line in self:
            if line.state == "second":
                raise UserError(
                    _("Cannot delete any record in confirmed state.")
                )
            elif line.move_id:
                line.move_id.state = "cancel"
                line.move_id.unlink()
        return super(AccountAnalyticStockMove, self).unlink()
