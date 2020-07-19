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

"""Concepts to invoice analytic accounts"""

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

MONTHS = {
    "1": _("Enero"),
    "2": _("Febrero"),
    "3": _("Marzo"),
    "4": _("Abril"),
    "5": _("Mayo"),
    "6": _("Junio"),
    "7": _("Julio"),
    "8": _("Agosto"),
    "9": _("Septiembre"),
    "10": _("Octubre"),
    "11": _("Noviembre"),
    "12": _("Diciembre"),
}


class AccountAnalyticInvoiceConcept(models.Model):
    """Concepts to invoice analytic accounts"""

    _name = "account.analytic.invoice.concept"
    _description = "Analytic account invoice concepts"

    @api.model
    def name_search(self, name, args=[], operator="ilike", limit=100):
        if name:
            concepts = self.search([("code", "=", name)] + args, limit=limit)
            if not concepts:
                concepts = self.search(
                    [("code", operator, name)] + args, limit=limit
                )
                concepts += self.search(
                    [("name", operator, name)] + args, limit=limit
                )
        else:
            concepts = self.search(args, limit=limit)

        return concepts.name_get()

    @api.model
    def process_name(self, description=False, date=False):
        if not description and not self:
            raise UserError(_(""))
        if not date:
            date = datetime.now()
        if not description:
            description = self.name
        return description.replace("%(year)s", str(date.year)).replace(
            "%(month)s", MONTHS[str(date.month)]
        )

    name = fields.Char("Concept", translate=True, required=True)
    code = fields.Char(size=8, required=True)
    product_id = fields.Many2one(
        "product.product",
        "Product",
        required=True,
        help="Product required to map invoice taxes.",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda r: r.env.user.company_id.id,
    )
