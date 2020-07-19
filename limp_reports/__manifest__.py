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
    "name": "Limpergal reports",
    "description": "Jasper Server reports for Limpergal.",
    "version": "11.0.1.0.0",
    "author": "Pexego",
    "website": "http://www.pexego.es",
    "category": "Reports",
    "depends": [
        "base",
        "limp_service_picking",
        "limp_contract",
        "jasper_reports",
        "report_py3o",
        "limp_custom",
        "analytic",
        "stock",
        "waste_management",
        "account_due_dates_str",
    ],
    "data": [
        "views/account_analytic_tag.xml",
        "views/res_company_view.xml",
        "views/res_users_view.xml",
        "limp_reports_data.xml",
        "views/menu_reports.xml",
        "wizard/wizard_print_memory.xml",
        "wizard/wizard_print_analytic_details_view.xml",
        "wizard/print_acceptance_document_view.xml",
        "data/acceptance_doc_seq.xml",
        "views/acceptance_document_view.xml",
        "report/analytic_detail_report.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
