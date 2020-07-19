##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos
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


class EmployeeIncidenceSetEndDateWzd(models.TransientModel):

    _name = "employee.incidence.set.end.date.wzd"

    date = fields.Date(required=True, default=fields.Date.today)
    only_incidences = fields.Boolean(
        help="Sets end date in incidences only, if not check it sets the end date in all open remunerations.",
        default=True,
    )

    @api.multi
    def act_set_end_date(self):
        employee_id = self._context.get("active_id", False)
        domain = [("employee_id", "=", employee_id), ("date_to", "=", False)]

        if self.only_incidences:
            domain.append(
                (
                    "incidence_id_tp",
                    "!=",
                    self.env.ref("analytic_incidences.incidence_normal").id,
                )
            )
        remunerations = self.env["remuneration"].search(domain)
        if remunerations:
            remunerations.write({"date_to": self.date})
        open_incidences = self.env["hr.laboral.incidence"].search(
            [("employee_id", "=", employee_id), ("end_date", "=", False)]
        )
        if open_incidences:
            open_incidences.write({"end_date": self.date})

        return {"type": "ir.actions.act_window_close"}
