# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
        "name" : "Scont management",
        "description": "Scont management",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Accounting",
        "depends" : [
            'base',
            'account',
            'hr',
            'limp_contract',
            'limp_service_picking',
            'invoice_concept',
            'limp_distribution_costs'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "data" : [
        #  'limp_contract_view.xml',
                        #  # 'account_invoice_view.xml',
                        #  'limp_service_picking_view.xml',
                        #  'wizard/remove_no_quality_view.xml',
                        #  # 'stock_picking_view.xml', MIGRACION:
                        #  'account_journal_view.xml',
                        #  'hr_employee_view.xml',
                        #  'timesheet_view.xml'
                        ],
        "installable": True,
        'active': False

}
