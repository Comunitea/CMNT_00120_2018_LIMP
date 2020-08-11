##############################################################################
#
#    Copyright (C) 2004-2013 Comunitea Servicios Tecnológicos S.L.
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Export account to glasof",
    "description": """Wizard to export account moves to Glasof""",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Account/Export",
    "depends": ["account"],
    "data": [
        "views/res_company_view.xml",
        "wizard/export_account_to_glasof_view.xml",
    ],
    "installable": True,
}
