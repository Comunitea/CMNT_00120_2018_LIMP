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
        "name" : "Recurrent employee's occupations to analytic accounts",
        "description": """Add new object employee's occupations to analytic accounts to manage employee tasks in reccurrent events""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Base/Contract",
        "depends" : [
            'base',
            'analytic',
            'account',
            'hr',
            'calendar'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                        'security/ir.model.access.csv',
                        'analytic_occupation_view.xml',
                        'security/analytic_occupation_security.xml'],
        "installable": True,
        'active': False

}
