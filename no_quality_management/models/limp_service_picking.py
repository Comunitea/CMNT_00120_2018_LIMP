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
from odoo import models, fields, api


class LimpServicePicking(models.Model):

    _inherit = "stock.service.picking"

    no_quality = fields.Boolean("Scont")

    def write(self, vals):
        res = super(LimpServicePicking, self).write(vals)
        if vals.get("no_quality", False):
            for pick in self:
                for line in pick.service_invoice_concept_ids:
                    line.write({"tax_ids": [(6, 0, [])]})
        return res

    def create_concept_lines(self):
        res = super(LimpServicePicking, self).create_concept_lines()
        for order in self:
            if order.no_quality:
                for line in order.service_invoice_concept_ids:
                    line.write({"tax_ids": [(6, 0, [])]})
        return res

    @api.onchange("intercompany")
    def onchange_intercompany(self):
        self.no_quality = self.intercompany
