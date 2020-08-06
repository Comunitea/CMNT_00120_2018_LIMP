##############################################################################
#
#    Copyright (C) 2004-2012 Comunitea Servicios Tecnológicos S.L.
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
    "name": "Distribution of costs",
    "description": """Sharing the costs of workers""",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Base/Laboral/Costs",
    "depends": [
        "hr",
        "analytic_incidences",
        "limp_account_analytic_extension",
        "limp_multi_delegations",
    ],
    "data": [
        "views/account_analytic_line_view.xml",
        "views/hr_employee_view.xml",
        "views/timesheet_view.xml",
        "wizard/distribution_costs_import_view.xml",
        "wizard/remuneration_timesheet_wzd_view.xml",
        "wizard/distribute_effective_costs_view.xml",
        "security/ir.model.access.csv",
        "security/limp_distribution_costs_security.xml",
        "data/timesheet_seq.xml",
    ],
    "installable": True,
}
