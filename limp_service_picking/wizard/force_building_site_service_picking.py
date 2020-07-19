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


class ForceBuildingSiteServicePicking(models.TransientModel):

    _name = "force.building.site.service.picking"

    service_picking_id = fields.Many2one(
        "stock.service.picking", "Picking", required=True
    )

    def copy_building_site(self):
        pickings = self.env["stock.service.picking"].browse(
            self._context.get("active_ids", [])
        )
        pickings.write(
            {"building_site_id": self.service_picking_id.building_site_id.id}
        )
        return {}
