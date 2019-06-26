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
            'invoice_concept',
            'analytic_incidences',
            'analytic_material_costs',
            'limp_service_picking',
            'limp_distribution_costs',
            'city_council',
            'limp_account_analytic_extension',
            'l10n_es_facturae'
            ],
        "data" : [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'data/contract_seq.xml',
            'views/limp_contract_signature_view.xml',
            'views/account_analytic_account_view.xml',
            'wizard/contract_to_invoice_view.xml',
            'views/limp_contract_view.xml',
            'views/limp_contract_line_cleaning_view.xml',
            'views/limp_contract_line_home_help_view.xml',
            'views/ir_sequence_view.xml',
            'views/limp_contract_line_task_rel_view.xml',
            'views/limp_contract_task_view.xml',
            'views/limp_incidence_view.xml',
            'security/limp_contract_security.xml',
            'views/analytic_invoice_concept_rel_view.xml',
            'views/hr_department_view.xml',
            'views/upamount_history_view.xml',
            'wizard/upamount_contract_view.xml',
            'wizard/update_last_invoice_date_view.xml',
            'views/analytic_stock_move_view.xml',
            'views/limp_contract_line_employee_task_view.xml',
            'views/hr_employee_view.xml',
            'views/stock_service_picking_view.xml',
            'views/account_invoice_view.xml',
            'views/res_company_view.xml',
            'data/maintenance_task_cron.xml',
            'views/limp_center_type_view.xml',
            'views/limp_contract_notes.xml',
            'views/maintenance_task.xml',
            'views/limp_contract_manual_ddd_view.xml',
            'limp_manual_ddd_report.xml',
            'data/months_interval.xml'
            ],
        "installable": True,

}
