##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    tax_product = fields.Boolean(
        related="product_id.tax_product", string="Tax product", readonly=True
    )


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    add_info = fields.Boolean(
        related="commercial_partner_id.add_info",
        string="Additional Information",
        readonly=True,
    )
    amount_taxes = fields.Float(
        "Tax amount",
        digits=dp.get_precision("Account"),
        compute="_compute_amount_taxes",
    )

    def action_invoice_open(self):
        journal_tag = self.journal_id.analytic_tag_id
        if journal_tag:
            for line in self.invoice_line_ids:
                if journal_tag not in line.analytic_tag_ids:
                    line.analytic_tag_ids = [(4, journal_tag.id)]
        return super(AccountInvoice, self).action_invoice_open()

    def _compute_amount_taxes(self):
        for invoice in self:
            amount_taxes = 0.0
            for line in invoice.invoice_line_ids.filtered(
                lambda l: l.tax_product
            ):
                amount_taxes += line.price_subtotal
            invoice.amount_taxes = amount_taxes


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def create(self, vals):
        if vals.get("ref", False) and "FACT. " not in vals["ref"]:
            vals["ref"] = "FACT. " + vals["ref"]
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        if vals.get("ref", False) and "FACT. " not in vals["ref"]:
            vals["ref"] = "FACT. " + vals["ref"]
        return super(AccountMove, self).write(vals)
