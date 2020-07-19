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


class AnalyticIncidenceWizard(models.TransientModel):

    _name = "analytic.incidence.wizard"

    date = fields.Date(required=True)
    date_to = fields.Date()
    incidence_id_tp = fields.Many2one("incidence", "Type")
    absence_id_tp = fields.Many2one("absence", "Type absence")
    conditions = fields.Selection(
        [
            ("equal_condition", "Equal conditions"),
            ("diff_condition", "Different conditions"),
        ],
        "Conditions",
        required=True,
        default="equal_condition",
    )
    with_contract = fields.Boolean("With contract")
    contract_hours = fields.Float("Hours", digits=(12, 2))
    with_hour_price = fields.Boolean("With hour price")
    hour_price_hours = fields.Float("Hours", digits=(12, 2))
    with_fix_qty = fields.Boolean("With fix qty")
    price = fields.Float(digits=(12, 2))
    quantity = fields.Float("Quantity", digits=(12, 2))
    ss_hours = fields.Float("SS hours", digits=(4, 2))
    ss_no_hours = fields.Float("No ss hours", digits=(4, 2))
    effective = fields.Float("Effective", digits=(12, 2))

    @api.multi
    def make_child_remunerations(self):
        self.ensure_one()
        vals = {}
        vals = {
            "with_contract": self.with_contract,
            "contract_hours": self.contract_hours,
            "with_hour_price": self.with_hour_price,
            "hour_price_hours": self.hour_price_hours,
            "with_fix_qty": self.with_fix_qty,
            "price": self.price,
            "quantity": self.quantity,
            "date": self.date,
            "incidence_id_tp": self.incidence_id_tp.id,
            "absence_id_tp": self.absence_id_tp.id,
            "date_to": self.date_to,
            "conditions": self.conditions,
            "ss_hours": self.ss_hours,
            "ss_no_hours": self.ss_no_hours,
            "effective": self.effective,
        }

        remunerations = self.env["remuneration"].browse(
            self._context.get("active_ids", [])
        )
        if remunerations:
            remunerations.make_child_inc_remuneration(vals)

        return {
            "type": "ir.actions.act_window_close",
        }
