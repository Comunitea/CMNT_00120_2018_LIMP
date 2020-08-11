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
from odoo import models, fields, api


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    delegation_id = fields.Many2one(
        "res.delegation",
        "Delegation",
        change_default=True,
        default=lambda r: r.env.user.context_delegation_id.id,
        index=True
    )
    department_id = fields.Many2one(
        "hr.department",
        "Department",
        change_default=True,
        default=lambda r: r.env.user.context_department_id.id,
        index=True
    )
    manager_id = fields.Many2one(
        "hr.employee",
        "Responsible",
        change_default=True,
        domain=[("responsible", "=", True)],
        default=lambda r: r.env.user.employee_ids
        and r.env.user.employee_ids[0].id
        or False,
        index=True
    )

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).finalize_invoice_move_lines(
            move_lines
        )
        for move_vals in move_lines:
            move_vals[2]["delegation_id"] = self.delegation_id.id
            move_vals[2]["department_id"] = self.department_id.id
            move_vals[2]["manager_id"] = self.manager_id.id
        return res

    @api.model
    def _get_refund_copy_fields(self):
        res = super()._get_refund_copy_fields()
        res += ['department_id', 'delegation_id', 'manager_id']
        return res
