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
from odoo import models, fields, api


class AccountanalyticDefault(models.Model):

    _inherit = "account.analytic.default"

    inv_type = fields.Selection(
        [
            ("out_invoice", "Customer Invoice"),
            ("in_invoice", "Supplier Invoice"),
            ("out_refund", "Customer Refund"),
            ("in_refund", "Supplier Refund"),
        ],
        "Type",
    )

    @api.model
    def account_get(
        self,
        product_id=None,
        partner_id=None,
        user_id=None,
        date=None,
        company_id=None,
    ):
        """
            Se sobreescribe la funcion para añadir el campo inv_type.
        """
        domain = []
        if self._context.get("inv_type"):
            domain += ["|", ("inv_type", "=", self._context["inv_type"])]
        domain += [("inv_type", "=", False)]
        if product_id:
            domain += ["|", ("product_id", "=", product_id)]
        domain += [("product_id", "=", False)]
        if partner_id:
            domain += ["|", ("partner_id", "=", partner_id)]
        domain += [("partner_id", "=", False)]
        if company_id:
            domain += ["|", ("company_id", "=", company_id)]
        domain += [("company_id", "=", False)]
        if user_id:
            domain += ["|", ("user_id", "=", user_id)]
        domain += [("user_id", "=", False)]
        if date:
            domain += [
                "|",
                ("date_start", "<=", date),
                ("date_start", "=", False),
            ]
            domain += [
                "|",
                ("date_stop", ">=", date),
                ("date_stop", "=", False),
            ]
        best_index = -1
        res = self.env["account.analytic.default"]
        for rec in self.search(domain):
            index = 0
            if rec.product_id:
                index += 1
            if rec.partner_id:
                index += 1
            if rec.company_id:
                index += 1
            if rec.user_id:
                index += 1
            if rec.inv_type:
                index += 1
            if rec.date_start:
                index += 1
            if rec.date_stop:
                index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res
