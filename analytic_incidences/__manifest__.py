# -*- coding: utf-8 -*-
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
{
    'name': 'Analytic laboral incidences',
    'description': """Allow creates laboral incidences""",
    'version': '1.0',
    'author': 'Pexego',
    'website': 'http://www.pexego.es',
    'category': 'Base/Laboral/Incidences',
    'depends': [
        'base',
        'hr',
        'account',
        'city_council',
        'invoice_concept'
    ],
    'data': [
        'wizard/analytic_incidence_wzd.xml',
        'views/absence.xml',
        'views/hr_employee.xml',
        'views/incidence.xml',
        'views/remuneration.xml',
        'wizard/employee_incidence_set_end_date_view.xml',
        'wizard/employee_replacement_wzd.xml',
        'data/incidence_data.xml',
        'wizard/employee_set_laboral_incidence_wzd.xml',
        'data/remuneration_sequence.xml',
        'security/ir.model.access.csv',
        'security/analytic_incidences_security.xml',
    ],
    'installable': True,

}
