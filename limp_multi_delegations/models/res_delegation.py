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
from odoo.exceptions import ValidationError


class ResDelegation(models.Model):

    _name = "res.delegation"
    _description = "Delegation"

    name = fields.Char("Delegation", size=32, required=True)
    code = fields.Char(size=8)
    description = fields.Text()
    parent_id = fields.Many2one("res.delegation", "Parent delegation")
    child_ids = fields.One2many(
        "res.delegation", "parent_id", "Child delegations"
    )
    user_ids = fields.Many2many(
        "res.users",
        "res_delegation_users_rel",
        "delegation_id",
        "user_id",
        "Related users",
    )
    address_id = fields.Many2one("res.partner", "Delegation Address")

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion("parent_id"):
            raise ValidationError(
                _("Error! You cannot create recursive delegations.")
            )
