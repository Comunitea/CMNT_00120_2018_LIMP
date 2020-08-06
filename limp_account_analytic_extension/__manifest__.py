##############################################################################
#
#    Copyright (C) 2004-2013 Comunitea Servicios Tecnológicos S.L.
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
    "name": "Analytic account extension",
    "description": """Extends analytic accounting for doing analysis""",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Account/Analytic",
    "depends": [
        "account",
        "analytic_base_department",
        "limp_multi_delegations",
        "account_analytic_default",
        "l10n_es_account_asset",
    ],
    "data": [
        "views/account_analytic_plans.xml",
        "views/account_analytic_default.xml",
        "views/account_analytic.xml",
        "views/account_asset.xml",
        "views/account_invoice.xml",
        "views/account_move_line.xml",
        "security/analytic_extension_security.xml",
    ],
    "installable": True,
}
