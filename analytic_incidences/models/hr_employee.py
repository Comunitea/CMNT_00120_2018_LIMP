# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiéira Saavedra$
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


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    def _compute_active_remunerations(self):
        current_date = fields.Date.today()
        for employee in self:
            remunerations = self.env['remuneration'].search(
                [('employee_id', '=', employee.id), '|',
                 ('date_to', '=', False), ('date_to', '>=', current_date)])
            employee.active_remunerations = remunerations and True or False

    laboral_incidence_ids = fields.One2many(
        'hr.laboral.incidence', 'employee_id', 'Incidences', readonly=True)
    work_council_id = fields.Many2one('city.council', 'Work council')
    active_remunerations = fields.Boolean(
        compute='_compute_active_remunerations')
