# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
        "name" : "Holiday calendar",
        "description": """Links holidays calendars to an employee with different scopes, It allows imports *.ics files too.""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "HR/Holidays",
        "depends" : [
            'base',
            'hr',
            'l10n_es_toponyms',
            'l10n_es_toponyms_region',
            'city_council'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                'hr_holiday_menu.xml',
                'hr_holiday_calendar_view.xml',
                'hr_holiday_view.xml',
                'wizard/import_ics_view.xml',
                'security/ir.model.access.csv'],
        "installable": True,
        'active': False

}
