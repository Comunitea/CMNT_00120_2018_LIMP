##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
    "name": "Containers management",
    "description": """Allow to manage containers, move with customers and moves history.""",
    "version": "12.0.1.0.0",
    "author": "Pexego",
    "website": "http://www.pexego.es",
    "category": "Base/Containers",
    "depends": ["base", "product", "stock", "hr"],
    "data": [
        "views/container.xml",
        "views/container_move.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
        "data/containers_sequence.xml",
        "security/container_security.xml",
    ],
    "installable": True,
}
