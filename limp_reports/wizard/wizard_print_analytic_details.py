##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, _
import time


class accountnalyticAccountDetails(models.TransientModel):
    _name = "account.analytic.account.details"

    date1 = fields.Date(
        "Start of period",
        required=True,
        default=lambda r: time.strftime("%Y-01-01"),
    )
    date2 = fields.Date(
        "End of period", required=True, default=fields.Date.today
    )
    department_id = fields.Many2one("hr.department", "Department")
    delegation_id = fields.Many2one("res.delegation", "Delegation")
    manager_id = fields.Many2one(
        "hr.employee", "Responsible", domain=[("responsible", "=", True)]
    )
    header = fields.Char(
        "Title of report",
        size=255,
        required=True,
        default=_("Analytic Details"),
    )
    detail = fields.Boolean("Show details")
    without_pickings = fields.Boolean(
        "Without pickings in contract", default=True
    )

    def print_report(self):
        data = self.read()[0]
        datas = {
            "ids": self.env.context.get("active_ids", []),
            "model": "account.analytic.account",
            "form": data,
        }
        records = self.env["account.analytic.account"].browse(
            self.env.context.get("active_ids", [])
        )
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', "limp_reports.account_analytic_details")], limit=1)
        return report.report_action(records, data=datas)
