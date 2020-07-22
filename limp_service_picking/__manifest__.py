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
    "name": "Services picking for Limpergal",
    "description": """Add new type of pickings for managing Limpergal's services""",
    "version": "12.0.1.0.0",
    "author": "Pexego",
    "website": "http://www.pexego.es",
    "category": "Contract/Picking",
    "depends": [
        "base",
        "stock",
        "containers_management",
        "simple_fleet_management",
        "waste_management",
        "product",
        "hr",
        "hr_timesheet",
        "analytic",
        "account",
        "limp_account_analytic_extension",
        "limp_distribution_costs",
        "limp_multi_delegations",
        "analytic_material_costs",
        "report_py3o",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "wizard/service_order_toinvoice_view.xml",
        "data/limp_service_picking_data.xml",
        "views/limp_service_picking_line_view.xml",
        "views/limp_service_picking_view.xml",
        "views/product_view.xml",
        "views/res_partner_view.xml",
        "data/product_data.xml",
        "views/building_site_services_view.xml",
        "views/limp_sporadic_service_picking_view.xml",
        "views/valorization_lines_view.xml",
        "wizard/add_to_invoice_view.xml",
        "views/fleet_view.xml",
        "data/analytic_tag_data.xml",
        "wizard/distribute_fleet_expense_view.xml",
        "views/stock_picking_view.xml",
        "wizard/force_building_site_service_picking_view.xml",
        "views/res_company_view.xml",
        "views/timesheet_view.xml",
        "views/account_journal_view.xml",
        "views/account_invoice_view.xml",
        "views/account_analytic_distribution.xml",
        "wizard/stock_invoice_onshipping.xml",
        "views/stock_service_picking_ddd.xml",
        "data/types_ddd.xml",
        "views/detected_species.xml",
        "views/products_used.xml",
        "data/ir_sequence_data.xml",
        "data/type_of_installation_legionella.xml",
        "views/legionella_samples.xml",
        "views/types_ddd_view.xml",
        "limp_service_picking_report.xml",
        "views/equipment_to_be_used_view.xml",
        "views/machinery_to_employ_view.xml",
        "views/observation_recommendation_ddd_view.xml",
    ],
    "installable": True,
}
