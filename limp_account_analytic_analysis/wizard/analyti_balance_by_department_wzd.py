##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos
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


class AnalyticBalanceByDepartment(models.TransientModel):
    _name = "analytic.balance.by.department.wzd"

    year = fields.Integer(
        default=lambda r: int(time.strftime("%Y")), required=True
    )
    delegation_id = fields.Many2one("res.delegation", "Delegation")
    privacy = fields.Selection([("public", "Public"), ("private", "Private")])

    @api.multi
    def print_report(self):
        data = self.read([])[0]
        data.update({"ids": self.ids})

        return {
            "type": "ir.actions.report",
            "report_name": "analytic_balance_by_department_xls",
            "datas": data,
        }
