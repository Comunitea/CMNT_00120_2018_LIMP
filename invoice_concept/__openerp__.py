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
        "name" : "Analytic account invoiced by concepts",
        "description": """Add new object invoice concept to analytic account to invoice by concepts""",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Base/Invoice/Contract",
        "depends" : [
            'base',
            'analytic',
            'account',
            'product'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                        'security/ir.model.access.csv',
                        'security/invoice_concept_security.xml',
                        'analytic_invoice_concept_view.xml',
                        'analytic_invoice_concept_rel_view.xml',
                        'account_invoice_view.xml',
                        'analytic_account_view.xml',
                        'wizard/contract_to_invoice_view.xml',
                        'product_view.xml'
                        ],
        "installable": True,
        'active': False

}
