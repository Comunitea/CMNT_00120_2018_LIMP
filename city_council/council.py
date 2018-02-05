#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

from openerp import models, fields
import wizard
import pooler


class city_council(models.Model):

    _name = 'city.council'

    _columns = {
        'name': fields.char('Council', size=64, required=True, select=1),
    }

city_council()

class city(models.Model):

    _inherit = "city.city"

    _columns = {
        'council_id': fields.many2one('city.council', 'Council')
    }

city()

class city_council2(models.Model):

    _inherit = 'city.council'

    _columns = {
        'city_ids': fields.one2many('city.city', 'council_id', 'Zipcodes'),
    }

city_council2()


'''class res_partner_address(models.Model):
    _inherit = "res.partner.address"

    _columns = {
        'council_id': fields.many2one('city.council', 'Council'),
    }

    def on_change_fields(self, cr, uid, ids, zipcode):
        if zipcode:
            cities = self.pool.get('city.city').search(cr, uid, [('zipcode', '=', zipcode)])
            if cities:
                city = self.pool.get('city.city').browse(cr, uid, cities[0])
                return {'value': {'location': city.id,
                                    'council_id': city.council_id and city.council_id.id or False,
                                    'city': city.name,
                                    'state_id': city.state_id.id,
                                    'country_id':city.state_id.country_id.id,
                                    'region': city.state_id.region_id and city.state_id.region_id.id or False
                                    }}

        return {}

res_partner_address() MIGRACION: Eliminado modelo res.partner.address'''

council_end_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Councils">
    <separator string="Result:" colspan="4"/>
    <label string="The councils has been associated successfully to the Spanish zip codes." colspan="4" align="0.0"/>
</form>'''

class l10n_es_associate_council_city(wizard.interface):
    def _associate_zipcode(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        for c in pool.get('city.city').browse(cr, uid, pool.get('city.city').search(cr, uid, [])):
            ids = pool.get('city.council').search(cr, uid, [('name', '=', c.name)])
            if not ids:
                council_id = pool.get('city.council').create(cr, uid, {'name': c.name})
            else:
                council_id = ids[0]
            c.write({'council_id': council_id})

            address_ids = pool.get('res.partner.address').search(cr, uid, [('location', '=', c.id)])
            if address_ids:
                pool.get('res.partner.address').write(cr, uid, address_ids, {'council_id': council_id})

        return {}

    states = {
        'init': {
            'actions': [_associate_zipcode],
            'result': {
                'type':'form',
                'arch':council_end_form,
                'fields': {},
                'state':[('end', 'Ok', 'gtk-ok'),]
            }
        }

    }
l10n_es_associate_council_city('city_council.asscociate_zipcode')
