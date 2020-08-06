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
from odoo import models, fields, api


class EmployeeSetLaboralIncidenceWzd(models.TransientModel):

    _name = "employee.set.laboral.incidence.wzd"

    @api.model
    def _get_default_employee(self):
        """returns current location ID"""
        if self._context.get("employee_id", False):
            return int(self._context["active_id"])
        return False

    employee_id = fields.Many2one(
        "hr.employee", "Employee", required=True, default=_get_default_employee
    )
    date = fields.Date(required=True, default=fields.Date.today)
    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Account", readonly=True
    )
    date_to = fields.Date()
    incidence_id_tp = fields.Many2one("incidence", "Type")
    absence_id_tp = fields.Many2one("absence", "Type absence")
    conditions = fields.Selection(
        [
            ("equal_condition", "Equal conditions"),
            ("diff_condition", "Different conditions"),
        ],
        required=True,
        default="equal_condition",
    )
    with_contract = fields.Boolean()
    contract_hours = fields.Float("Hours", digits=(12, 2))
    with_hour_price = fields.Boolean()
    hour_price_hours = fields.Float("Hours", digits=(12, 2))
    with_fix_qty = fields.Boolean()
    price = fields.Float(digits=(12, 2))
    quantity = fields.Float(digits=(12, 2))
    ss_hours = fields.Float("SS hours", digits=(4, 2))
    ss_no_hours = fields.Float("No ss hours", digits=(4, 2))
    effective = fields.Float(digits=(12, 2))
    distribute_bt_remuneration = fields.Boolean(
        "Distribute between remunerations",
        help="Distribute quantities between all "
        "selected remuneration proportionally to original hours",
    )

    @api.multi
    def set_incidence(self):
        vals = {}
        employees_ids = self._context.get("active_ids", [])
        if employees_ids:
            obj = self.env["hr.employee"].browse(employees_ids[0])

        for line_child_remu in self:
            type_incidence_id = self.env.ref(
                "analytic_incidences.incidence_absence"
            ).id
            vals = {
                "with_contract": line_child_remu.with_contract,
                "contract_hours": line_child_remu.contract_hours,
                "with_hour_price": line_child_remu.with_hour_price,
                "hour_price_hours": line_child_remu.hour_price_hours,
                "ss_hours": line_child_remu.ss_hours,
                "ss_no_hours": line_child_remu.ss_no_hours,
                "with_fix_qty": line_child_remu.with_fix_qty,
                "price": line_child_remu.price,
                "quantity": line_child_remu.quantity,
                "date": line_child_remu.date,
                "incidence_id_tp": type_incidence_id,
                "absence_id_tp": line_child_remu.absence_id_tp.id,
                "date_to": line_child_remu.date_to or False,
                "conditions": line_child_remu.conditions,
                "effective": line_child_remu.effective,
                "distribute_bt_remuneration":
                line_child_remu.distribute_bt_remuneration,
            }

            type_incidence_normal_id = self.env.ref(
                "analytic_incidences.incidence_normal"
            ).id
            parent_remuneration_id = self.env["remuneration"].search(
                [
                    ("employee_id", "=", obj.id),
                    ("incidence_id_tp", "=", type_incidence_normal_id),
                    "|",
                    ("date_to", "=", False),
                    ("date_to", ">=", line_child_remu.date),
                ]
            )

            if parent_remuneration_id:
                parent_remuneration_id.make_child_inc_remuneration(vals)

                self.env["hr.laboral.incidence"].create(
                    {
                        "initial_date": line_child_remu.date,
                        "end_date": line_child_remu.date_to,
                        "motive": line_child_remu.absence_id_tp.id,
                        "employee_id": obj.id,
                    }
                )
        result = self.env.ref(
            "analytic_incidences.action_remuneration_tree"
        ).read()[0]
        result["domain"] = [
                ("employee_id", "=", obj.id),
                ("date", ">=", line_child_remu.date),
                "|",
                ("date_to", ">=", line_child_remu.date_to),
                ("date_to", "=", False),
            ]
        return result
