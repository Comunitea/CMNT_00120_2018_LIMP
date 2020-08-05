##############################################################################
#
#    Copyright (C) 2004-2011 Comunitea Servicios Tecnológicos S.L.
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
    "name": "Multi Delegations",
    "description": "Add new dimension for multi-company rules, delegations.",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Base/Multi-company",
    "depends": ["hr",],
    "data": [
        "views/res_delegation_view.xml",
        "views/res_users_view.xml",
        "views/hr_employee.xml",
        "security/ir.model.access.csv",
        "security/multi_delegations_security.xml",
    ],
    "installable": True,
}
