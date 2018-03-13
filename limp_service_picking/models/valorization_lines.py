# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields

class ValorizationLines(models.Model):
    _name = "valorization.lines"
    _auto = False
    _rec_name = 'ler_code_id'
    _order = "date desc"

    date = fields.Date('Date')
    qty = fields.Float("Quantity (T)",readonly=True)
    volume = fields.Float("Volume (m³)",readonly=True)
    company_id =fields.Many2one('res.company','Company',readonly=True)
    building_site_id =fields.Many2one('building.site.services','Building',readonly=True)
    product_id =fields.Many2one('product.product','Product',readonly=True)
    product_name =fields.Char('Product Name',readonly=True,size=256)
    producer_promoter =fields.Char('Producer',readonly=True,size=256)
    holder_builder = fields.Char('Holder', size=255, readonly=True)
    vat_holder = fields.Char('Vat', size=32, readonly=True)
    ler_code_id =fields.Many2one('waste.ler.code',string="LER", readonly=True)
    ler_name = fields.Char('LER name', related='ler_code_id.name', readonly=True)
    picking_ler = fields.Char('Picking LER', size=32, readonly=True)
    building_nif = fields.Char(string='Producer N.I.F/C.I.F', related='building_site_id.vat_producer')
    building_city = fields.Char(string='Council', related='building_site_id.city_producer')
    building_province = fields.Char(string='Province', related='building_site_id.province_producer')
    partner_id = fields.Many2one('res.partner', "Customer", readonly=True)
    picking_id = fields.Many2one('stock.service.picking', 'Picking', readonly=True)
    memory_include = fields.Boolean('Memory include', readonly=True)
    manager_partner_id = fields.Many2one('res.partner', "Manager", readonly=True)
    no_computed = fields.Boolean('No computed')
    stock_picking_id = fields.Many2one('stock.picking', 'Stock picking', readonly=True)

    def init(self):
        self.env.cr.execute("""
            create or replace view valorization_lines as (
            SELECT S.retired_date AS date,V.id AS id,coalesce(V.net_weight,0.0) AS qty,
            (coalesce(V.product_qty,0.0) + coalesce(V.overload_qty,0.0)) as volume, coalesce(SP.company_id, A.company_id) as company_id,S.building_site_id,V.product_id,V.name as product_name,B.producer_promoter,V.ler_code as picking_ler,
            P2.ler_code_id,A.partner_id,B.holder_builder,B.vat_holder,S.id as picking_id, V.memory_include, S.manager_partner_id, V.no_compute as no_computed, SP.id as stock_picking_id
            FROM service_picking_valorization_rel AS V
                INNER JOIN stock_service_picking as S ON V.service_picking_id = S.id
                INNER JOIN account_analytic_account as A ON S.analytic_acc_id = A.id
                LEFT JOIN building_site_services AS B ON S.building_site_id = B.id
                INNER JOIN product_product AS P ON V.product_id = P.id
                INNER JOIN product_template AS P2 ON P.product_tmpl_id = P2.id
                LEFT JOIN waste_ler_code as L on P2.ler_code_id = L.id
                LEFT JOIN stock_picking AS SP on SP.stock_service_picking_id = S.id
            )""")
