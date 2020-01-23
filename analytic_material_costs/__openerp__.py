# -*- coding: utf-8 -*-
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
        "name" : "Analytic account material costs",
        "description": """Add intermediate object between analytic_account and stock_move to adding material costs in analytic lines""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Base/Contract",
        "depends" : [
            'base',
            'analytic',
            'account',
            'stock',
            'hr'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : ['analytic_material_costs_data.xml',
                    'analytic_stock_move_view.xml',
                    'hr_employee_view.xml',
                    'analytic_account_view.xml',
                    'security/ir.model.access.csv'],
        "installable": True,
        'active': False

}