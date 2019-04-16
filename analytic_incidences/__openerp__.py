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
        "name" : "Analytic laboral incidences",
        "description": """Allow creates laboral incidences""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Base/Laboral/Incidences",
        "depends" : [
            'base',
            'hr',
            'account',
            'account_analytic_plans',
            'analytic_occupations',
            'city_council'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
            'remuneration_sequence.xml',
            'incidence_data.xml',
            'absence_view.xml',
            'incidence_view.xml',
            'wizard/analytic_incidence_wzd.xml',
            'wizard/employee_replacement_wzd.xml',
            'wizard/search_employee_replacement_wzd.xml',
            'wizard/employee_set_laboral_incidence_wzd.xml',
            #'wizard/analytic_incidence_set_end_date_view.xml',
            'remuneration_view.xml',
            'security/ir.model.access.csv',
            'hr_employee_view.xml',
            'laboral_incidences_view.xml',
            'analytic_occupation_view.xml',
            'security/analytic_incidences_security.xml',
            'wizard/employee_incidence_set_end_date_view.xml'
        ],
        "installable": True,
        'active': False

}