##############################################################################
#
#    Copyright (C) 2004-2011 Comunitea Servicios Tecnonólicos S.L.
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
    "name": "Multi Departments",
    "description": "*Many2many to relate departments and users.",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "http://www.pexego.es",
    "category": "Base/Multi-company",
    "depends": ["hr"],
    "data": [
        "views/hr_department.xml",
        "views/res_users.xml",
        "security/multi_departments_security.xml",
    ],
    "installable": True,
}
