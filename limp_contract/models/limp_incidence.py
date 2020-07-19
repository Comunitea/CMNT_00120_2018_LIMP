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
from odoo import models, fields
from odoo.addons import decimal_precision as dp


class LimpIncidence(models.Model):

    _name = "limp.incidence"
    _description = "Incidences"

    periodicity = fields.Selection(
        [
            ("q", "Quarterly"),
            ("ex", "Exception"),
            ("w", "Weekly"),
            ("bm", "Bimonthly"),
            ("m", "Monthly"),
            ("2m", "Two months"),
        ],
        "Frequency",
        default="ex",
    )
    incidence_date = fields.Date(
        "Date", required=True, default=fields.Date.today
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Customer",
        required=True,
        default=lambda r: r._context.get("partner_id", False),
    )
    contract_line_id = fields.Many2one(
        "limp.contract.line", "Contract line", readonly=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        readonly=True,
        default=lambda r: r._context.get("company_id", False),
    )
    department_id = fields.Many2one(
        "hr.department",
        "Department",
        default=lambda r: r._context.get("department_id", False),
    )
    delegation_id = fields.Many2one(
        "res.delegation",
        "Delegation",
        default=lambda r: r._context.get("delegation_id", False),
    )
    department_code = fields.Char(
        "Dep.", related="department_id.code", readonly=True
    )
    picking_id = fields.Many2one("stock.picking", "Picking")
    employee_id = fields.Many2one("hr.employee", "Worker", required=True)
    hours = fields.Float("Hours")
    amount = fields.Float(
        "Amount",
        help="Amount per hours",
        digits=dp.get_precision("Account"),
        readonly=True,
    )
    name = fields.Char("Description", size=256, required=True)
    next_date = fields.Date("Next date")
    note = fields.Text("Notes")
