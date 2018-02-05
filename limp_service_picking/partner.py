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

from osv import osv, fields

class res_partner(osv.osv):

    _inherit = 'res.partner'

    _columns = {
        'partner_contact_id': fields.many2one('res.partner', 'Partner contact'),
        'authorization_no': fields.char('Authorization no.', size=32),
        'manager_authorization_no': fields.text('Manager authorization no.'),
        'transport_authorization_no': fields.char('Transport authorization no.', size=32),
        'destination_manager': fields.boolean('Destination manager', help="Check this box if the partner is a destination manager."),
        'building_site_services_ids': fields.many2many('building.site.services', 'partner_building_site_services_rel', 'partner_ids', 'building_site_services_id', 'Building sites/Services'),
        'nima_no': fields.char('NIMA', size=255),
        'create_nima_number': fields.boolean('Create nima number', help="Create nima number in service pickings")
    }

res_partner()
