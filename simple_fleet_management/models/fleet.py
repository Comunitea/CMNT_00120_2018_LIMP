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

from odoo import models, fields, api, _


class Fleet(models.Model):

    _name = "fleet"
    _description = "Fleet"
    _rec_name = "license_plate"

    type = fields.Selection(
        [
            ("truck", "Truck"),
            ("car", "Car"),
            ("van", "Van"),
            ("other", "Other"),
        ],
        "Type",
        required=True,
        help="Vehicle type",
        default="truck",
    )
    name = fields.Char("Name", required=True)
    license_plate = fields.Char(size=18, required=True)
    note = fields.Text("Description")
    expense_ids = fields.One2many(
        "fleet.expense",
        "fleet_id",
        "Expenses",
        domain=[("distribute", "=", True)],
    )
    expense_no_distribute_ids = fields.One2many(
        "fleet.expense",
        "fleet_id",
        "No Distribute expenses",
        domain=[("distribute", "=", False)],
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda r: r.env.user.company_id.id,
    )
    avg_consumption = fields.Float(
        "Average consumption", compute="_compute_avg_consumption"
    )
    start_date = fields.Date(store=False)
    end_date = fields.Date(store=False)

    _sql_constraints = [
        (
            "license_plate_uniq",
            "unique (license_plate)",
            _("The license plate must be unique !"),
        ),
    ]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """allows search by center name too"""
        if args is None:
            args = []

        if name:
            fleets = self.search(
                [
                    "|",
                    ("license_plate", operator, name),
                    ("name", operator, name),
                ]
                + args,
                limit=limit,
            )
        else:
            fleets = self.search(args, limit=limit)
        return fleets.name_get()

    def _compute_avg_consumption(self):
        domain = []
        type_expense_id = self.env.ref(
            "simple_fleet_management.fleet_expense_type_refueling"
        ).id

        if self._context.get("start_date", False):
            domain.append(("expense_date", ">=", self._context["start_date"]))
        if self._context.get("end_date", False):
            domain.append(("expense_date", "<=", self._context["end_date"]))
        if domain:
            for fleet in self:
                domain2 = [
                    ("expense_type", "=", type_expense_id),
                    ("fleet_id", "=", fleet.id),
                ]
                domain2.extend(domain)
                expenses = (
                    self.env["fleet.expense"]
                    .search(domain2)
                    .filtered("consumption")
                )
                if expenses:
                    fleet.avg_consumption = sum(
                        expenses.mapped("consumption")
                    ) / len(expenses)
