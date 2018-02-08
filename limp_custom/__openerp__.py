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
        "name" : "Customization for Limpergal",
        "description": """Limpergal's customizations""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Custom",
        "depends" : [
            'base',
            'account',
            'analytic',
            'stock',
            'warning',
            'product',
            'hr',
            # 'base_iban',
            'multi_departments',
            'base_contact',
            'limp_service_picking',
            'purchase',
            'account_payment_extension',
            'account_analytic_plans',
            'limp_multi_delegations',
            'limp_account_analytic_extension',
            # 'account_payment_sepa_direct_debit',
            'containers_management',
            'limp_contract',
            'l10n_es_facturae',
            'account_analytic_analysis',
            'limp_distribution_costs'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [#'stock_picking_view.xml', MIGRACION: Vistas stock
                        'product_view.xml',
                        'security/limp_custom_data.xml',
                        'res_partner_view.xml',
                        # 'purchase_view.xml', MIGRACION: warehouse_id ya no existe cambiar por picking_type_id?
                        'invoice_lines_view.xml',
                        'account_invoice_view.xml',
                        'security/ir.model.access.csv',
                        'hr_employee_view.xml',
                        'container_view.xml',
                        'res_users_view.xml',
                        'account_analytic_view.xml'],
        "installable": True,
        'active': False

}
