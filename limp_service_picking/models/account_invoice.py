##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
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


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    building_site_id = fields.Many2one(
        "building.site.services", "Building Site"
    )
    service_picking_id = fields.Many2one(
        "stock.service.picking", "Service picking", readonly=True
    )
    move_id = fields.Many2one("stock.move", "Move")
    quantity = fields.Float("Quantity", digits=(12, 3), required=True)


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    intercompany = fields.Boolean("Intercompany", readonly=True)
    intercompany_invoice_id = fields.Many2one(
        "account.invoice", "Intercompany invoice", readonly=True
    )

    @api.model
    def _refund_cleanup_lines(self, lines):
        res = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        for line in res:
            line[2]["building_site_id"] = (
                line[2].get("building_site_id", False)
                and line[2]["building_site_id"][0]
            )
            line[2]["service_picking_id"] = (
                line[2].get("service_picking_id", False)
                and line[2]["service_picking_id"][0]
            )

        return res


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    invoice_line_ids = fields.One2many(
        "account.invoice.line",
        "service_picking_id",
        "Invoice lines",
        readonly=True,
    )
    invoice_id = fields.Many2one(
        "account.invoice",
        "Invoice",
        related="invoice_line_ids.invoice_id",
        readonly=True,
    )


class AccountJournal(models.Model):

    _inherit = "account.journal"

    intercompany = fields.Boolean("Intercompany")
