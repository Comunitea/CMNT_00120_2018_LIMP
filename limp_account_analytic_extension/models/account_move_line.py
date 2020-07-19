##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    delegation_id = fields.Many2one(
        "res.delegation",
        "Delegation",
        default=lambda r: r.env.user.context_delegation_id.id,
    )
    department_id = fields.Many2one(
        "hr.department",
        "Department",
        default=lambda r: r.env.user.context_department_id.id,
    )
    manager_id = fields.Many2one(
        "hr.employee",
        "Responsible",
        domain=[("responsible", "=", True)],
        default=lambda r: r.env.user.employee_ids
        and r.env.user.employee_ids[0].id
        or False,
    )

    def _prepare_analytic_line(self):
        res = super(AccountMoveLine, self)._prepare_analytic_line()
        for vals_dict in res:
            vals_dict["delegation_id"] = self.delegation_id.id
            vals_dict["department_id"] = self.department_id.id
            vals_dict["manager_id"] = self.manager_id.id
            vals_dict["company_id"] = self.company_id.id
        return res
