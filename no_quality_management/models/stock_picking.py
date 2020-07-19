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


class StockPicking(models.Model):

    _inherit = "stock.picking"

    no_quality = fields.Boolean("Scont")

    def action_invoice_create(self, journal_id, group, date):
        if group:
            if any([x.no_quality for x in self]):
                raise UserError("Scont pickings can't be grouped")
        return super(StockPicking, self).action_invoice_create(
            journal_id, group, date
        )
