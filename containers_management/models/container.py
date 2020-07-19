##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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


class Container(models.Model):

    _name = "container"
    _description = "Containers"
    _rec_name = "code"

    code = fields.Char("Code", size=10, readonly=True)
    type = fields.Selection(
        [
            ("flat_dumpster15", "Flat Dumpster 1,5"),
            ("flat_dumpster3", "Flat Dumpster 3"),
            ("flat_dumpster4", "Flat Dumpster 4"),
            ("flat_dumpster7", "Flat Dumpster 7"),
            ("flat_dumpster9", "Flat Dumpster 9"),
            ("flat_dumpster12", "Flat Dumpster 12"),
            ("flat_dumpster14", "Flat Dumpster 14"),
            ("flat_dumpster18", "Flat Dumpster 18"),
            ("flat_dumpster30", "Flat Dumpster 30"),
            ("trapezoidal4", "Trapezoidal 4"),
            ("trapezoidal6", "Trapezoidal 6"),
            ("trapezoidal8", "Trapezoidal 8"),
            ("other", "Other"),
        ],
        "Type",
        required=True,
        default="flat_dumpster9",
    )
    shape = fields.Selection(
        [("opened", "Opened"), ("closed", "Closed")],
        "Shape",
        required=True,
        default="opened",
    )
    dimensions = fields.Char("Dimensions", size=32)
    capacity = fields.Float(
        "Capacity (m³)", digits=dp.get_precision("Product UoM")
    )
    note = fields.Text("Observations")
    active = fields.Boolean("Active", default=True)
    history_ids = fields.One2many(
        "container.move", "container_id", "History", readonly=True
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda r: r.env.user.company_id.id
    )
    last_move_date = fields.Datetime("Last move date", readonly=True)
    last_responsible_id = fields.Many2one(
        "hr.employee", "Last driver", readonly=True
    )
    situation_id = fields.Many2one(
        "res.partner",
        "Situation",
        help="Current situation, customer address or available "
        "in company addresses",
        default=lambda r: r.env.user.company_id.partner_id.address_get().get(
            "default", False
        ),
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        readonly=True,
        related="situation_id.commercial_partner_id",
    )
    home = fields.Boolean(
        "Home", related="situation_id.containers_store", readonly=True
    )
    container_placement = fields.Selection(
        [("on_street", "On street"), ("on_building", "On building")],
        string="Container placement",
    )

    @api.multi
    def write(self, vals):
        """creates the registry in the history"""
        if vals.get("situation_id", False) and not self._context.get(
            "no_create_moves", False
        ):
            for container in self:
                if not container.situation_id:
                    self.env["container.move"].create(
                        {
                            "container_id": container.id,
                            "move_type": "out",
                            "address_id": vals["situation_id"],
                            "move_date": vals.get(
                                "last_move_date", fields.Datetime.now()
                            ),
                            "responsible_id": vals.get(
                                "last_responsible_id", False
                            ),
                        }
                    )
                elif vals["situation_id"] != container.situation_id.id:
                    self.env["container.move"].create(
                        {
                            "container_id": container.id,
                            "move_type": "out",
                            "address_id": container.situation_id.id,
                            "move_date": vals.get(
                                "last_move_date", fields.Datetime.now()
                            ),
                            "responsible_id": vals.get(
                                "last_responsible_id", False
                            ),
                        }
                    )
                    self.env["container.move"].create(
                        {
                            "container_id": container.id,
                            "move_type": "in",
                            "address_id": vals["situation_id"],
                            "move_date": vals.get(
                                "last_move_date", fields.Datetime.now()
                            ),
                            "responsible_id": vals.get(
                                "last_responsible_id", False
                            ),
                        }
                    )

        return super(Container, self).write(vals)

    @api.model
    def create(self, vals):
        sequence = ""
        if vals.get("type", False):
            if "flat_dumpster" in vals["type"]:
                sequence_code = "container_flat_dumpster{}".format(
                    vals["type"].split("flat_dumpster")[1]
                )
            elif "trapezoidal" in vals["type"]:
                sequence_code = "container_trapezoidal{}".format(
                    vals["type"].split("trapezoidal")[1]
                )
            elif vals["type"] == "other":
                sequence_code = "container_other"
            sequence = self.env["ir.sequence"].next_by_code(sequence_code)

        if sequence:
            vals["code"] = sequence
        return super(Container, self).create(vals)
