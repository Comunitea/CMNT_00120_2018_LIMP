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
        "name" : "Limpergal reports",
        "description": "Jasper Server reports for Limpergal.",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Reports",
        "depends" : [
            'base',
            'limp_service_picking',
            'limp_contract',
            'jasper_reports',
            'report_aeroo_ooo',
            'limp_custom',
            'analytic',
            'stock',
            'waste_management'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                'limp_reports_data.xml',
                'res_company_view.xml',
                'annual_memory.xml',
                'menu_reports.xml',
                'wizard/wizard_print_memory.xml',
                'wizard/wizard_print_hours_report_view.xml',
                'wizard/wizard_print_analytic_details_view.xml',
                'wizard/print_acceptance_document_view.xml',
                'acceptance_doc_seq.xml',
                'acceptance_document_view.xml',
                'security/ir.model.access.csv',
                'res_users_view.xml'
            ],
        "installable": True,
        'active': False

}
