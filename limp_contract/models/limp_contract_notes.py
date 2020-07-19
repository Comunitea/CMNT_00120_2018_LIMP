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


class LimpContractNote(models.Model):

    _name = "limp.contract.note"
    _order = "date desc"

    date = fields.Date("Date", required=True, default=fields.Date.today)
    name = fields.Text("Description", required=True)
    user_id = fields.Many2one(
        "res.users", "User", readonly=True, default=lambda r: r.env.user.id
    )
    contract_id = fields.Many2one("limp.contract", "Contract")
