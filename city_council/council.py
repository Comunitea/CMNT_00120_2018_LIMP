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
# import wizard
# # import pooler MIGRACION: Comentado


class CityCouncil(models.Model):

    _name = 'city.council'

    name = fields.Char('Council', required=True)
    zip_ids = fields.One2many('res.better.zip', 'council_id', 'Zipcodes')


class ResBetterZip(models.Model):

    _inherit = "res.better.zip"

    council_id = fields.Many2one('city.council', 'Council')


council_end_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Councils">
    <separator string="Result:" colspan="4"/>
    <label string="The councils has been associated successfully to the Spanish zip codes." colspan="4" align="0.0"/>
</form>'''
'''
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
l10n_es_associate_council_city('city_council.asscociate_zipcode')'''
