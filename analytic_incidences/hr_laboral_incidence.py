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

"""History of employee's laboral incidences"""

from openerp import models, fields

class HrLaboralIncidence(models.Model):
    """History of employee's laboral incidences"""

    _name = "hr.laboral.incidence"
    _description = "Laboral Incidence"
    _rec_name = 'motive'


    initial_date = fields.Date(readonly=True)
    end_date = fields.Date(readonly=True)
    motive = fields.Many2one('absence', 'Motive', readonly=True)
    employee_id = fields.Many2one('hr.employee', readonly=True)
    # occupation_ids = fields.One2many('account.analytic.occupation', 'incidence_id', 'Occupations', readonly=True) Migracion: Ocupaciones fuera
