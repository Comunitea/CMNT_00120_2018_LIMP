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

from odoo import models, fields
from odoo.addons import decimal_precision as dp


class FleetExpense(models.Model):

    _name = "fleet.expense"
    _description = "Fleet expenses"
    _order = "km desc, expense_date desc"

    expense_date = fields.Date(
        "Date", required=True, default=fields.Date.today
    )
    name = fields.Char("Description", required=True)
    fleet_id = fields.Many2one("fleet", "Vehicle", required=True)
    fleet_owner_id = fields.Many2one("res.partner", "Owner",
                                     related="fleet_id.owner_id")
    amount = fields.Float(digits=dp.get_precision("Account"), required=True)
    net_amount = fields.Float(
        digits=dp.get_precision("Account"), compute="_compute_net_amount"
    )
    note = fields.Text()
    expense_type = fields.Many2one(
        "fleet.expense.type", "Type", help="Expense type"
    )
    partner_id = fields.Many2one("res.partner", "Supplier")
    labor = fields.Float(digits=dp.get_precision("Account"))
    parts_price = fields.Float(digits=dp.get_precision("Account"))
    liter = fields.Float(digits=dp.get_precision("Account"))
    km = fields.Float(digits=dp.get_precision("Account"))
    distribute = fields.Boolean(default=True)
    department_id = fields.Many2one(
        "hr.department",
        "Department",
        required=True,
        default=lambda r: r._context.get(
            "c_department_id",
            r._context.get(
                "department_id", r.env.user.context_department_id.id
            ),
        ),
        index=True
    )
    consumption = fields.Float(
        "Consumption (l/100Km)",
        digits=(13, 2),
        help="Liters each 100 km. (Refuel liters / traveled km) * 100",
        compute="_compute_consumption",
    )

    def _compute_net_amount(self):
        for expense in self:
            if expense.expense_type.product_id:
                net_amount = sum(
                    [
                        x.with_context(force_price_include=True).
                        _compute_amount(
                            expense.amount,
                            expense.amount,
                            1,
                            product=expense.expense_type.product_id or False,
                            partner=expense.partner_id or False,
                        )
                        for x in expense.expense_type.
                        product_id.supplier_taxes_id
                    ]
                )
                if net_amount:
                    expense.net_amount = expense.amount - net_amount
                    continue
            expense.net_amount = expense.amount

    def _compute_consumption(self):
        type_expense_id = self.env.ref(
            "simple_fleet_management.fleet_expense_type_refueling"
        ).id
        for expense in self:
            if (
                expense.expense_type
                and expense.expense_type.id == type_expense_id
            ):
                expense_old = self.search(
                    [
                        ("km", "<", expense.km),
                        ("expense_type", "=", type_expense_id),
                        ("fleet_id", "=", expense.fleet_id.id),
                    ],
                    limit=1,
                )
                if expense_old and expense_old.km and expense.km:
                    expense.consumption = (
                        expense.liter / (expense.km - expense_old.km)
                    ) * 100.0
                    continue
            expense.consumption = 0.0
