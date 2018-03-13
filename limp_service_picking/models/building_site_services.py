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
from odoo import models, fields, api


class BuildingSiteServices(models.Model):
    _name = "building.site.services"
    _description = "Building sites/Services."

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            obj = self.search(
                ['|','|','|','|','|','|','|','|','|','|','|','|','|','|',
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
                 ('address_building_site.street', 'ilike', name)], limit=limit)
        else:
            obj = self.search(args, limit=limit)

        return obj.name_get()

    name = fields.Char('Name', compute='_compute_address_name')
    producer_promoter = fields.Char('Producer/Promoter', size=255)
    address_producer = fields.Char('Adress', size=148)
    vat_producer = fields.Char('Vat',size=32)
    city_producer = fields.Char('City', size=64)
    province_producer = fields.Char('Province', size=64)
    holder_builder = fields.Char('Holder/Builder', size=255)
    address_holder = fields.Char('Address', size=148)
    vat_holder = fields.Char('Vat', size=32)
    city_holder = fields.Char('City', size=64)
    province_holder = fields.Char('Province', size=64)
    address_building_site = fields.Many2one('res.partner','Address')
    contact_id = fields.Many2one('res.partner', 'Contact')
    building_site_license = fields.Char('License nº', size=64)
    city_building_site = fields.Char('City', size=64)
    #identification_manager = fields.Char('Manager', size=148),
    #authorization_no = fields.Char('Authorization no.', size=32, required=True),
    partner_ids = fields.Many2many('res.partner', 'partner_building_site_services_rel', 'building_site_services_id','partner_ids', 'Partner')
    show = fields.Selection([('building', 'Building'),('service', 'Service')],'Show', required=True, deafault='building')
    code = fields.Char('Reference/Order', size=128)
    serial = fields.Char('Code', size=128)
    pricelist_id = fields.Many2one("product.pricelist","Pricelist")
    active = fields.Boolean('Active', default=True)
    admission_no = fields.Char('Admission no.', size=24, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, default=lambda r: r._context.get('company_id', self.env.user.company_id.id))
    description = fields.Char('Description', size=128)

    '''
    _defaults = {
        #'identification_manager':  lambda self, cr, uid, context: context.get('identification_manager', False),
        #'authorization_no':  lambda self, cr, uid, context: context.get('authorization_no', False),
    }'''


    def _compute_address_name(self):
        for obj in self:
            if obj.address_building_site:
                obj.name = obj.address_building_site.name_get()[0][1]
            elif obj.contact_id:
                obj.name = (obj.contact_id.first_name and (obj.contact_id.first_name + u" ") or u"") + obj.contact_id.name
            else:
                obj.name = ""

    @api.model
    def create(self, vals):
        if self._context.get('partner_id', False):
            vals['partner_ids'] = [(4, context['partner_id'])]
        admission_seq = self.env['ir.sequence'].next_by_code('waste.admission.number')
        vals['admission_no'] = admission_seq

        return super(BuildingSiteServices, self).create(vals)
