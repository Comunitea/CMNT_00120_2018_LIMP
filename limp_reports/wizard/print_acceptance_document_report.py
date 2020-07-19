##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields


class PrintAcceptanceDocumentReport(models.TransientModel):

    _name = "print.acceptance.document.report"

    building_site_id = fields.Many2one(
        "building.site.services", "Building Site / Service", required=True
    )
    waste_id = fields.Many2one("waste.ler.code", "LER", required=True)

    def print_report(self):
        """prints report"""
        acceptance_ids = self.env["acceptance.document"].search(
            [
                ("building_site_id", "=", self.building_site_id.id),
                ("waste_id", "=", self.waste_id.id),
            ]
        )
        if acceptance_ids:
            data = acceptance_ids[0].read()
            accept_ids = [acceptance_ids[0].id]
        else:
            admission_seq = self.env["ir.sequence"].next_by_code(
                "acceptance_document"
            )
            new_waste = self.env["acceptance.document"].create(
                {
                    "building_site_id": self.building_site_id.id,
                    "waste_id": self.waste_id.id,
                    "number": admission_seq,
                }
            )
            data = new_waste.read()
            accept_ids = [new_waste.id]

        datas = {"ids": accept_ids}
        datas["model"] = "acceptance.document"
        datas["form"] = data
        return {
            "type": "ir.actions.report",
            "report_name": "acceptance_document",
            "datas": datas,
        }
