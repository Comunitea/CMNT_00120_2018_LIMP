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


class LimpContractLine(models.Model):

    _name = "limp.contract.line"
    _description = "Limpergal's contract lines"
    _rec_name = "num"

    contract_id = fields.Many2one(
        "limp.contract", "Contract", readonly=True, ondelete="cascade"
    )
    num = fields.Char("Num.", size=4, readonly=True)
    amount = fields.Float(
        "Amount", digits=dp.get_precision("Account"), readonly=True
    )
    employee_task_ids = fields.One2many(
        "limp.contract.line.employee.task",
        "contract_line_id",
        "Employees Tasks",
    )
    note = fields.Text("Description")
    incidences = fields.Boolean("Contents incidences")
    incidences_text = fields.Text("Incidences description")
