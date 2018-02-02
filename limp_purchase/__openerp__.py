# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos
#    $Omar Castiñeira Saavedra$
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
        "name" : "Limpergal purchase report",
        "description": "Purchase report cutomization.",
        "version" : "1.0",
        "author" : "Comunitea",
        "website" : "http://www.comunitea.com",
        "category" : "Purchases",
        "depends" : [
            'purchase',
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : ['limp_purchase_report.xml',
                        'purchase_view.xml'],
        "installable": True,
        'active': False
}
