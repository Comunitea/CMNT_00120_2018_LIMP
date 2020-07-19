##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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
from odoo import models, fields, api, _


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    glasof_code = fields.Char("Code in Glasof", size=7)
    responsible = fields.Boolean()

    @api.multi
    def name_get(self):
        res = []
        for employee in self:
            name = employee.name
            if employee.glasof_code:
                name = u"[" + employee.glasof_code + u"] " + name
                if not employee.active_remunerations:
                    name = u"[DESACTIVADO] " + name
            res.append((employee.id, name))
        return res

    _sql_constraints = [
        (
            "glasof_code_uniq",
            "unique (glasof_code)",
            _("The Glasof code must be unique !"),
        ),
    ]
