##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
import time
import calendar
from odoo.tools import ustr


class DistributionEffectiveCosts(models.TransientModel):
    _name = "distribution.effective.costs"

    name = fields.Char("Name", size=64, required=True)
    month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        "Month",
        required=True,
    )
    year = fields.Integer(
        "Year", required=True, default=lambda r: int(time.strftime("%Y"))
    )

    def distribute_costs(self):
        year = str(self.year)
        month = str(self.month).zfill(2)

        first_day, last_day = calendar.monthrange(
            int(year), int(month)
        )  # obtenemos el último días del mes
        sueldos_tag = self.env["account.analytic.tag"].search(
            [("name", "=", "Sueldos")]
        )
        general_account_id = self.env["account.account"].search(
            [("code", "=", "64000000")]
        )

        for employee in self.env["hr.employee"].search([]):
            # obtenemos los parte de horas del empleado dentro del mes importado
            timesheets = self.env["timesheet"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("date", ">=", year + "-" + month + "-01"),
                    ("date", "<=", year + "-" + month + "-" + str(last_day)),
                    ("done", "=", True),
                ]
            )
            for timesheet in timesheets:
                if timesheet.analytic_id:
                    duplicated_lines = self.env[
                        "account.analytic.line"
                    ].search(
                        [
                            ("timesheet_id", "=", timesheet.id),
                            ("account_id", "=", timesheet.analytic_id.id),
                            (
                                "name",
                                "=",
                                ustr(self.name)
                                + u" (effective)/ "
                                + month
                                + u"/"
                                + year
                                + u"/ "
                                + employee.name,
                            ),
                        ]
                    )  # borramos duplicados
                    if duplicated_lines:
                        duplicated_lines.unlink()
                    amount = timesheet.effective
                    if amount:
                        vals = {
                            "amount": -(amount),
                            "name": ustr(self.name)
                            + u" (effective)/ "
                            + month
                            + u"/"
                            + year
                            + u"/ "
                            + employee.name,
                            "tag_ids": [(4, sueldos_tag[0].id)],
                            "timesheet_id": timesheet.id,
                            "account_id": timesheet.analytic_id.id,
                            "general_account_id": general_account_id[0].id,
                            "date": year
                            + "/"
                            + month
                            + "/"
                            + str(
                                calendar.monthrange(int(year), int(month))[1]
                            ),
                            "department_id": timesheet.department_id
                            and timesheet.department_id.id
                            or (
                                timesheet.analytic_id.department_id
                                and timesheet.analytic_id.department_id.id
                                or False
                            ),
                            "delegation_id": timesheet.delegation_id
                            and timesheet.delegation_id.id
                            or (
                                timesheet.analytic_id.delegation_id
                                and timesheet.analytic_id.delegation_id.id
                                or False
                            ),
                            "manager_id": timesheet.responsible_id
                            and timesheet.responsible_id.id
                            or (
                                timesheet.analytic_id.manager_id
                                and timesheet.analytic_id.manager_id.id
                                or False
                            ),
                            "employee_id": employee.id,
                            "company_id": self.env.user.company_id.id,
                        }
                        self.env["account.analytic.line"].create(vals)

        return {"type": "ir.actions.act_window_close"}
