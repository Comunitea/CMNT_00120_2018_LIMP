##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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


class AccountInvoiceReport(models.Model):

    _inherit = "account.invoice.report"

    privacy = fields.Selection(
        [("public", "Public"), ("private", "Private")],
        "Privacy",
        readonly=True,
    )
    delegation_id = fields.Many2one(
        "res.delegation", "Delegation", readonly=True
    )
    department_id = fields.Many2one(
        "hr.department", "Department", readonly=True
    )
    manager_id = fields.Many2one(
        "hr.employee",
        "Responsible",
        readonly=True,
        domain=[("responsible", "=", True)],
    )
    no_quality = fields.Boolean("Scont", readonly=True)

    def _select(self):
        res = super(AccountInvoiceReport, self)._select()
        res += """
            , sub.privacy as privacy, sub.delegation_id as delegation_id,
            sub.department_id as department_id,
            sub.manager_id as manager_id, sub.no_quality as no_quality"""
        return res

    def _sub_select(self):
        res = super(AccountInvoiceReport, self)._sub_select()
        res += """
            , ai.privacy as privacy, ai.delegation_id as delegation_id,
            ai.department_id as department_id,
            ai.manager_id as manager_id, ai.no_quality as no_quality"""
        return res

    def _group_by(self):
        res = super(AccountInvoiceReport, self)._group_by()
        res += """
            , ai.privacy , ai.delegation_id ,
            ai.department_id ,
            ai.manager_id, ai.no_quality"""
        return res
