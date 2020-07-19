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
from dateutil.relativedelta import relativedelta
from datetime import datetime


class UpamountContractWzd(models.TransientModel):
    _name = "upamount.contract.wzd"

    upamount_percent = fields.Float(
        "Upamount (%)", digits=(12, 3), required=True
    )

    def _reg_upamount(
        self, contract, upamount_percent, previous_amount, new_amount, name
    ):
        return self.env["limp.contract.upamount.history"].create(
            {
                "contract_id": contract.id,
                "name": name,
                "upamount_percent": upamount_percent,
                "previous_amount": previous_amount,
                "new_amount": new_amount,
            }
        )

    def _update_concepts(self, analytical_acc, upamount_percent, contract):
        for concept in analytical_acc.concept_ids:
            vals = {}
            if concept.amount:
                vals["amount"] = concept.amount + (
                    concept.amount * (upamount_percent / 100.0)
                )
                self._reg_upamount(
                    contract,
                    upamount_percent,
                    concept.amount,
                    vals["amount"],
                    analytical_acc.name
                    + u" Normal: "
                    + concept.concept_id.name,
                )
            concept.write(vals)
        return True

    def upamount_action(self):
        contracts = self.env["limp.contract"].search(
            [
                ("id", "in", self._context.get("active_ids", [])),
                ("active", "=", True),
                ("state", "not in", ("close", "cancelled")),
            ]
        )
        for contract in contracts:
            # Annual amount
            if contract.amount:
                new_amount = contract.amount + (
                    contract.amount * (self.upamount_percent / 100.0)
                )
                contract.write({"amount": new_amount})
                self._reg_upamount(
                    contract,
                    self.upamount_percent,
                    contract.amount,
                    new_amount,
                    contract.name + _(u": Annual amount"),
                )

            # contract invoice concepts
            self._update_concepts(
                contract.analytic_account_id, self.upamount_percent, contract
            )

            for home_line in contract.home_help_line_ids:
                self._update_concepts(
                    home_line.analytic_acc_id, self.upamount_percent, contract
                )
            for clean_line in contract.cleaning_line_ids:
                self._update_concepts(
                    clean_line.analytic_acc_id, self.upamount_percent, contract
                )

            contract.write(
                {
                    "upamount_date": (
                        datetime.now() + relativedelta(years=+1)
                    ).strftime("%Y-%m-%d")
                }
            )
        return {"type": "ir.actions.act_window_close"}
