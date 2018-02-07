# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
        "name" : "Limpergal contracts",
        "description": "Add contract model for Limpergal.",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Contracts",
        "depends" : [
            'base',
            'analytic',
            'limp_multi_delegations',
            'hr',
            'stock',
            'account',
            'decimal_precision',
            'base_contact',
            'base_contact_extend',
            'analytic_department',
            'analytic_occupations',
            'account_payment_extension',
            'invoice_concept',
            'hr_holiday_calendar',
            'analytic_incidences',
            'analytic_material_costs',
            'limp_service_picking',
            'limp_distribution_costs',
            'city_council',
            'limp_account_analytic_extension',
            'l10n_es_facturae'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'contract_seq.xml',
            'limp_contract_signature_view.xml',
            'account_analytic_account_view.xml',
            'wizard/contract_to_invoice_view.xml',
            'limp_contract_view.xml',
            'limp_contract_line_cleaning_view.xml',
            'limp_contract_line_home_help_view.xml',
            'ir_sequence_view.xml',
            'limp_contract_line_task_rel_view.xml',
            'limp_contract_task_view.xml',
            'limp_incidence_view.xml',
            'security/limp_contract_security.xml',
            'analytic_occupation_view.xml',
            'account_analytic_occupation_name_view.xml',
            'analytic_invoice_concept_rel_view.xml',
            'hr_department_view.xml',
            'upamount_history_view.xml',
            'wizard/upamount_contract_view.xml',
            'wizard/update_last_invoice_date_view.xml',
            'analytic_stock_move_view.xml',
            #'limp_contract_line_waste_view.xml',
            'account_invoice_report_view.xml',
            'limp_contract_line_employee_task_view.xml',
            'hr_employee_view.xml',
            'stock_service_picking_view.xml',
            'account_invoice_view.xml',
            'res_company_view.xml',
            'maintenance_task_cron.xml',
            'limp_center_type_view.xml'
            ],
        "installable": True,
        'active': False

}
