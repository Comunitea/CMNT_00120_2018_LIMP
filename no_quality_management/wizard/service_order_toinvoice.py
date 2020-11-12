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
from odoo import models


class ServiceOrderToInvoice(models.TransientModel):

    _inherit = "service.order.toinvoice"

    def create_invoice(self):
        res = super(ServiceOrderToInvoice, self).create_invoice()
        for record in res:
            rec = self.env["stock.service.picking"].browse(record)
            if rec.no_quality:
                invoice = self.env["account.invoice"].browse(res[record])
                invoice.write({"no_quality": True})
        return res
