##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos S.L.
#    $Omar Castiñeira Saavedra$ omar@comunitea.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields


class create_service_picking_from_sale(models.TransientModel):

    _name = "create.service.picking.from.sale"

    picking_type = fields.Selection(
        [
            ("wastes", "Wastes"),
            ("sporadic", "Sporadic"),
            ("maintenance", "Maintenance"),
        ],
        "Service picking type",
        required=True,
    )

    def action_create_picking(self):
        sale = self.env["sale.order"].browse(
            self._context.get("active_id", [])
        )
        res = sale.with_context(picking_type=self.picking_type).create_pick()
        return res
