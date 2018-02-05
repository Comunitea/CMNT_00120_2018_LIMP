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
        "name" : "Partner extension",
        "description": "Add some improvements in partners.",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Base/Partner",
        "depends" : [
            'base',
            'base_contact',
            'l10n_es_partner',
            'base_vat_unique',
            'calendar'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
            'partner_view.xml',
            'partner_address_view.xml',
            #'res_partner_job_view.xml' MIGRACION: Modelo res.partner.job eliminado
        ],
        "installable": True,
        'active': False

}
