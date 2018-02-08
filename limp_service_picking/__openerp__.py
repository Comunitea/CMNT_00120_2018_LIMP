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
        "name" : "Services picking for Limpergal",
        "description": """Add new type of pickings for managing Limpergal's services""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Contract/Picking",
        "depends" : [
            'base',
            'stock',
            'containers_management',
            'simple_fleet_management',
            'waste_management',
            'base_contact',
            'product',
            'hr',
            'hr_timesheet',
            'analytic',
            'account',
            "account_payment",
            "account_payment_extension",
            "account_analytic_plans",
            'limp_account_analytic_extension',
            'limp_distribution_costs',
            'limp_multi_delegations'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : ['security/groups.xml',
                        'service_picking_stock_move_view.xml',
                        'security/ir.model.access.csv',
                         'wizard/service_order_toinvoice_view.xml',
                        'limp_service_picking_data.xml',
                        'limp_service_picking_line_view.xml',
                        'limp_service_picking_view.xml',
                        'product_view.xml',
                        'res_partner_view.xml',
                        'waste_services_view.xml',
                        'service_picking_employees_rel_view.xml',
                        'product_data.xml',
                        'building_site_services_view.xml',
                        'limp_sporadic_service_picking_view.xml',
                        'valorization_lines_view.xml',
                        'stock_service_picking_seq.xml',
                        'wizard/add_to_invoice_view.xml',
                        'fleet_view.xml',
                        'data/analytic_journal_data.xml',
                        'wizard/distribute_fleet_expense_view.xml',
                        #'stock_picking_view.xml',
                        'wizard/force_building_site_service_picking_view.xml',
                        'res_company_view.xml',
                        'timesheet_view.xml',
                        'account_journal_view.xml',
                        'account_invoice_view.xml',
                       ],
        "installable": True,
        'active': False

}
