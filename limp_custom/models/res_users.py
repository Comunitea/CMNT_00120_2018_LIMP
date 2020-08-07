##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields


class res_users(models.Model):

    _inherit = "res.users"

    work_address_id = fields.Many2one("res.partner", string="Work Address")
    context_responsible_id = fields.Many2one(
        "hr.employee", "Resposible", domain=[("responsible", "=", True)],
        index=True
    )
