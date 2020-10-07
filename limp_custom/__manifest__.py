##############################################################################
#
#    Copyright (C) 2004-2011 Comunitea Servicios Tecnológicos S.L.
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
    "name": "Customization for Limpergal",
    "description": """Limpergal's customizations""",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Custom",
    "depends": [
        "account_invoice_currency",
        "multi_departments",
        "limp_service_picking",
        "purchase",
        "limp_multi_delegations",
        "limp_account_analytic_extension",
        "containers_management",
        "limp_contract",
        "l10n_es_facturae",
        "limp_distribution_costs",
        "account_payment_mode",
        "stock_secondary_unit"
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/product_view.xml",
        "security/limp_custom_data.xml",
        "views/res_partner_view.xml",
        "views/invoice_lines_view.xml",
        "views/account_invoice_view.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "views/container_view.xml",
        "views/res_users_view.xml",
        "views/account_analytic_view.xml",
        "views/account_journal.xml",
    ],
    "installable": True,
}
