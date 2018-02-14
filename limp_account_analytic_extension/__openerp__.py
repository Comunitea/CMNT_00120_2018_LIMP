# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
        "name" : "Analytic account extension",
        "description": """Extends analytic accounting for doing analysis""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Account/Analytic",
        "depends" : [
            'base',
            'analytic',
            'account',
            'analytic_department',
            'limp_multi_delegations',
            'account_analytic_plans',
            'account_analytic_default',
            'account_payment_extension',
            'l10n_es_account_asset',
            'account_analytic_analysis'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "data" : ['security/analytic_extension_security.xml',
                        'security/ir.model.access.csv',
                        # 'account_invoice_view.xml', MIGRACION:
                        'account_analytic_plans_view.xml',
                        'account_analytic_view.xml',
                        'account_analytic_report_entries_view.xml',
                        'account_move_line_view.xml',
                        'account_asset_view.xml'],
        "installable": True,
        'active': False

}
