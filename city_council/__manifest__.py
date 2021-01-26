##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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
    "name": "Council city",
    "version": "12.0.2.0.0",
    "author": "Comunitea",
    "category": "Generic Modules/Base",
    "description": """Council to classify cities (zipcodes)""",
    "depends": ["base_location", "sales_team", "analytic", "contacts"],
    "data": [
        "views/res_partner.xml",
        "views/council.xml",
        "views/res_country_region_view.xml",
        "security/ir.model.access.csv",
        "data/res_country_region_data.xml"
    ],
    "installable": True,
}
