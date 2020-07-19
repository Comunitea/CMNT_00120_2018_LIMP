##############################################################################
#
#    Copyright (C) 2014 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, api
import time


class AnalyticBalance(models.TransientModel):
    _name = "analytic.balance"

    year = fields.Integer(
        default=lambda r: int(time.strftime("%Y")), required=True
    )
    delegation_id = fields.Many2one("res.delegation", "Delegation")
    department_id = fields.Many2one("hr.department", "Department")
    manager_id = fields.Many2one(
        "hr.employee", "Responsible", domain=[("responsible", "=", True)]
    )
    privacy = fields.Selection([("public", "Public"), ("private", "Private")])

    @api.multi
    def print_report(self):
        selected_targets = []
        for tag in self.env["account.analytic.tag"].search(
            [("show_in_report", "=", True)]
        ):
            target_domain = [
                ("analytic_tag_id", "=", tag.id),
                ("year", "=", self.year),
            ]
            if self.delegation_id:
                target_domain.extend(
                    [
                        "|",
                        ("delegation_id", "=", self.delegation_id.id),
                        ("delegation_id", "=", False),
                    ]
                )
            else:
                target_domain.append(("delegation_id", "=", False))
            if self.department_id:
                target_domain.extend(
                    [
                        "|",
                        ("department_id", "=", self.department_id.id),
                        ("department_id", "=", False),
                    ]
                )
            else:
                target_domain.append(("department_id", "=", False))
            if self.manager_id:
                target_domain.extend(
                    [
                        "|",
                        ("manager_id", "=", self.manager_id.id),
                        ("manager_id", "=", False),
                    ]
                )
            else:
                target_domain.append(("manager_id", "=", False))

            target_ids = self.env["account.analytic.target"].search(
                target_domain
            )
            if target_ids:
                not_perfect_targets = {}
                for target in target_ids:
                    if (
                        target.delegation_id
                        and target.department_id
                        and target.manager_id
                    ):
                        selected_targets.append(target.id)
                        break
                    else:
                        not_perfect_targets[target.id] = 0
                        if target.manager_id:
                            not_perfect_targets[target.id] += 5
                        if target.department_id:
                            not_perfect_targets[target.id] += 3
                        if target.delegation_id:
                            not_perfect_targets[target.id] += 1

                if not_perfect_targets:
                    best_target = False
                    for target in not_perfect_targets:
                        if (
                            not best_target
                            or best_target[1] < not_perfect_targets[target]
                        ):
                            best_target = (target, not_perfect_targets[target])
                    selected_targets.append(best_target[0])

        data = self.read([])[0]
        data.update({"target_ids": selected_targets})
        data.update({"ids": self._ids})

        return {
            "type": "ir.actions.report",
            "report_name": "analytic_balance_xls",
            "datas": data,
        }
