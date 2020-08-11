##############################################################################
#
#    Copyright (C) 2014 Comunitea Servicios Tecnológicos S.L.
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
    "name": "Account Analytic Analysis Reports",
    "description": """Extends analytic accounting for doing analysis""",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Account/Analytic",
    "depends": [
        "analytic_base_department",
        "limp_multi_delegations",
        "limp_account_analytic_extension",
        "limp_reports",
        "date_range",
        "report_xlsx",
    ],
    "data": [
        "views/account_analytic_tag.xml",
        "analytic_analysis_report.xml",
        "wizard/analytic_balance_view.xml",
        "security/ir.model.access.csv",
        "security/account_analytic_analysis_security.xml",
        "wizard/analyti_balance_by_department_wzd_view.xml",
    ],
    "installable": True,
}
