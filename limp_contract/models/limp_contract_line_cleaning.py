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
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LimpContractLineCleaning(models.Model):

    _name = "limp.contract.line.cleaning"
    _description = "Limpergal's contract lines for cleaning"
    _inherits = {
        "limp.contract.line": "contract_line_id",
        "account.analytic.account": "analytic_acc_id",
    }

    contract_line_id = fields.Many2one(
        "limp.contract.line",
        "Contract line",
        readonly=True,
        required=True,
        ondelete="cascade",
    )
    analytic_acc_id = fields.Many2one(
        "account.analytic.account",
        "Analytic account",
        readonly=True,
        required=True,
        ondelete="cascade",
    )

    def open_line(self):
        return self.write({"state": "open"})

    def reopen_line(self):
        return self.write({"state": "open"})

    def get_all_tasks(self):
        for line in self:
            if not line.department_id:
                raise UserError(
                    _("Not department defined for this contract line")
                )
            task_ids = self.env["limp.contract.task"].search(
                [
                    "|",
                    ("department_id", "=", line.department_id.id),
                    ("department_id", "=", False),
                ]
            )
            for task in task_ids:
                task_rels = self.env["limp.contract.line.task.rel"].search(
                    [
                        ("contract_line_id", "=", line.contract_line_id.id),
                        ("contract_task_id", "=", task.id),
                    ]
                )
                if not task_rels:
                    self.env["limp.contract.line.task.rel"].create(
                        {
                            "contract_line_id": line.contract_line_id.id,
                            "contract_task_id": task.id,
                        }
                    )
        return True

    @api.onchange("address_id")
    def onchange_address_id(self):
        if self.address_id:
            vals = {}
            if self.address_id.state_id:
                self.state_id = self.address_id.state_id.id
            if self.address_id.council_id:
                self.location_id = self.address_id.council_id.id

    def copy(self, default=None):
        default = default or {}
        default.update(
            {
                "state": "draft",
                "date": False,
                "parent_id": False,
                "line_ids": [],
                "employee_ids": [],
                "active_employee_ids": [],
                "inactive_employee_ids": [],
                "report_employee_ids": [],
            }
        )

        return super(LimpContractLineCleaning, self.sudo()).copy(default)

    def copy_data(self, default=None):
        default = default or {}
        if context.get("is_contract", False):
            if self.date:
                return {}
        default.update(
            {
                "state": "draft",
                "date": False,
                "parent_id": False,
                "line_ids": [],
                "employee_ids": [],
                "active_employee_ids": [],
                "inactive_employee_ids": [],
                "report_employee_ids": [],
            }
        )
        return super(LimpContractLineCleaning, self).copy_data(default)

    @api.model
    def create(self, vals):
        if vals.get("contract_id", False):
            contract = self.env["limp.contract"].browse(vals["contract_id"])
            if contract.seq_lines_id:
                num = contract.seq_lines_id.next_by_id()
                vals["name"] = contract.name + u" - " + num
                vals["num"] = num
                if not vals.get("delegation_id", False):
                    vals["delegation_id"] = contract.delegation_id.id
                if not vals.get("department_id", False):
                    vals["department_id"] = contract.department_id.id
                if not vals.get("company_id", False):
                    vals["company_id"] = contract.company_id.id
                if not vals.get("parent_id", False):
                    vals["parent_id"] = contract.analytic_account_id.id
        else:
            raise UserError(_("Not contract defined for this line"))
        vals["invoiceable"] = True

        return super(LimpContractLineCleaning, self).create(vals)

    def write(self, vals):
        res = super(LimpContractLineCleaning, self).write(vals)
        if vals.get("date", False) or vals.get("date_start", False):
            all_remuneration_ids = self.env["remuneration"]
            remuneration_ids_wo_dateto = self.env["remuneration"]

            for line in self:
                all_remuneration_ids += line.remuneration_ids
                remuneration_ids_wo_dateto += line.remuneration_ids.filtered(
                    lambda r: not r.date_to
                )

            if all_remuneration_ids:
                if vals.get("date_start", False):
                    all_remuneration_ids.sudo().write(
                        {"date": vals["date_start"]}
                    )
                if vals.get("date", False) and remuneration_ids_wo_dateto:
                    remuneration_ids_wo_dateto.sudo().write(
                        {"date_to": vals["date"]}
                    )
        if vals.get("state", False) and vals["state"] in (
            "open",
            "close",
            "cancelled",
        ):
            for line in self:
                line.analytic_acc_id.state = vals["state"]
        return res

    def unlink(self):
        for line in self:
            if line.state not in ("draft", "cancelled"):
                raise UserError(
                    _(
                        "Only contract lines in draft or cancelled states can be deleted."
                    )
                )
        res = super(LimpContractLineCleaning, self).unlink()
        return res
