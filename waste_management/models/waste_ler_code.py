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


class WasteLerCode(models.Model):

    _name = "waste.ler.code"
    _description = "European list of waste"
    _rec_name = "code"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", size=10, required=True)
    dangerous = fields.Boolean("Dangerous")
    cpa = fields.Boolean("cpa")
    density = fields.Float("Density", digits=(16, 3), default=1.0)

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            wlc = self.search([("code", "ilike", name)] + args, limit=limit)
            if not wlc:
                name = name.split(" / ")[-1]
                wlc = self.search(
                    [("name", operator, name)] + args, limit=limit
                )
        else:
            wlc = self.search(args, limit=limit)
        return wlc.name_get()
