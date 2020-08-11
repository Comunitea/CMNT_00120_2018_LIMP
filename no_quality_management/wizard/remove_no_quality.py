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


class RemoveNoQuality(models.TransientModel):

    _name = "remove.no.quality"

    to_date = fields.Date("To date", required=True, default=fields.Date.today)

    def delete_no_quality(self):
        invoice_ids = (
            self.env["account.invoice"]
            .sudo()
            .search(
                [
                    ("no_quality", "=", True),
                    ("date_invoice", "<=", self.to_date),
                ]
            )
        )
        invoice_to_unlink = self.env["account.invoice"].sudo()
        for invoice in invoice_ids:
            if invoice.state in ("draft", "cancel"):
                invoice_to_unlink |= invoice
            elif invoice.state in ("proforma", "proforma2", "open"):
                if invoice.payment_ids:
                    invoice.payment_ids.cancel()
                    invoice.payment_ids.write({"move_name": ""})
                invoice.action_cancel()
                invoice_to_unlink |= invoice
            elif invoice.state == "paid":
                invoice.payment_ids.cancel()
                invoice.payment_ids.write({"move_name": ""})
                invoice.payment_ids.unlink()
                invoice.action_cancel()
                invoice_to_unlink |= invoice
        invoice_to_unlink.unlink()

        pickings_to_unlink = self.env['stock.service.picking'].sudo().\
            search([('no_quality', '=', True),
                    ('picking_date', '<=', self.to_date)])
        lines_to_unlink = self.env['stock.service.picking.line'].sudo().\
            search([('picking_id', 'in', pickings_to_unlink.ids)])
        lines_to_unlink.write({'state': 'draft'})
        lines_to_unlink.unlink()
        pickings_to_unlink.unlink()

        return {"type": "ir.actions.act_window_close"}
