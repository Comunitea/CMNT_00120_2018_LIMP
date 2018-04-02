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
    "name" : "Limpergal budgets",
    "description": "Add budget model for Limpergal.",
    "version" : "1.0",
    "author" : "Pexego",
    "website" : "http://www.pexego.es",
    "category" : "Budgets",
    "depends" : [
        'base',
        'sale',
        'product',
        'account',
        'limp_multi_delegations',
        'limp_service_picking',
        'limp_contract',
        ],
    "data" : [
        'wizard/create_service_picking_from_sale_view.xml',
        'views/sale_order_periodicity_view.xml',
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',
        'limp_sale_report.xml',
        'security/limp_sale_data.xml',
        'views/limp_service_picking_view.xml',
        'views/waste_services_view.xml',
        'views/limp_contract_view.xml',
        'report/sale_report.xml'
        ],
    "installable": True,

}
