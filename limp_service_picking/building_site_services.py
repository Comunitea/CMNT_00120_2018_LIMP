# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from openerp.osv import osv, fields

class building_site_services(osv.osv):
    _name = "building.site.services"
    _description = "Building sites/Services."

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        if name:
            ids = self.search(cr, uid, ['|','|','|','|','|','|','|','|','|','|','|','|','|','|',
                                        ('holder_builder', 'ilike', name),
                                        ('vat_producer', 'ilike', name),
                                        ('producer_promoter', 'ilike', name),
                                        ('city_building_site', 'ilike', name),
                                        ('address_holder', 'ilike', name),
                                        ('address_producer', 'ilike', name),
                                        ('vat_holder', 'ilike', name),
                                        ('province_producer', 'ilike', name),
                                        ('province_holder', 'ilike', name),
                                        ('city_holder', 'ilike', name),
                                        ('city_producer', 'ilike', name),
                                        ('code', 'ilike', name),
                                        ('serial', 'ilike', name),
                                        ('description', 'ilike', name),
                                        ('address_building_site.street', 'ilike', name)], limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)

        result = self.name_get(cr, uid, ids, context)
        return result

    def _get_address_name(self,cr,uid,ids,field_name,args,context={}):
        res = {}
        for obj in self.browse(cr,uid,ids,context=context):
            if obj.address_building_site:
                res[obj.id] = obj.address_building_site.name_get()[0][1]
            elif obj.contact_id:
                res[obj.id] = (obj.contact_id.first_name and (obj.contact_id.first_name + u" ") or u"") + obj.contact_id.name
            else:
                res[obj.id] = ""
        return res

    _columns = {
        'name': fields.function(_get_address_name, method=True, type="char",size=128, string='Name', readonly=True),
        'producer_promoter': fields.char('Producer/Promoter', size=255),
        'address_producer': fields.char('Adress', size=148),
        'vat_producer': fields.char('Vat',size=32),
        'city_producer': fields.char('City', size=64),
        'province_producer': fields.char('Province', size=64),
        'holder_builder': fields.char('Holder/Builder', size=255),
        'address_holder': fields.char('Address', size=148),
        'vat_holder': fields.char('Vat', size=32),
        'city_holder': fields.char('City', size=64),
        'province_holder': fields.char('Province', size=64),
        'address_building_site': fields.many2one('res.partner','Address'),
        'contact_id': fields.many2one('res.partner', 'Contact'),
        'building_site_license': fields.char('License nº', size=64),
        'city_building_site': fields.char('City', size=64),
        #'identification_manager': fields.char('Manager', size=148),
        #'authorization_no': fields.char('Authorization no.', size=32, required=True),
        'partner_ids': fields.many2many('res.partner', 'partner_building_site_services_rel', 'building_site_services_id','partner_ids', 'Partner'),
        'show': fields.selection([('building', 'Building'),('service', 'Service')],'Show', required=True),
        'code': fields.char('Reference/Order', size=128),
        'serial': fields.char('Code', size=128),
        'pricelist_id': fields.many2one("product.pricelist","Pricelist"),
        'active': fields.boolean('Active'),
        'admission_no': fields.char('Admission no.', size=24, readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'description': fields.char('Description', size=128)
    }
    _defaults = {
        #'identification_manager':  lambda self, cr, uid, context: context.get('identification_manager', False),
        #'authorization_no':  lambda self, cr, uid, context: context.get('authorization_no', False),
        'show': lambda *a: 'building',
        'active': lambda *a: True,
        'company_id': lambda self, cr, uid, context: context.get('company_id', False) or self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        if context.get('partner_id', False):
            vals['partner_ids'] = [(4,context['partner_id'])]
        admission_seq = self.pool.get('ir.sequence').get(cr, uid, 'waste.admission.number')
        vals['admission_no'] = admission_seq

        return super(building_site_services, self).create(cr, uid, vals, context=context)

building_site_services()
