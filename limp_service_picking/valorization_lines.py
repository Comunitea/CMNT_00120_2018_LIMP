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

from osv import fields,osv
import tools

class valorization_lines(models.Model):
    _name = "valorization.lines"
    _auto = False
    _rec_name = 'ler_code_id'
    _order = "date desc"
    _columns = {
        'date': fields.date('Date'),
        'qty':fields.float("Quantity (T)",readonly=True),
        'volume':fields.float("Volume (m³)",readonly=True),
        'company_id':fields.many2one('res.company','Company',readonly=True),
        'building_site_id':fields.many2one('building.site.services','Building',readonly=True),
        'product_id':fields.many2one('product.product','Product',readonly=True),
        'product_name':fields.char('Product Name',readonly=True,size=256),
        'producer_promoter':fields.char('Producer',readonly=True,size=256),
        'holder_builder': fields.char('Holder', size=255, readonly=True),
        'vat_holder': fields.char('Vat', size=32, readonly=True),
        'ler_code_id':fields.many2one('waste.ler.code',string="LER", readonly=True),
        'ler_name': fields.related('ler_code_id', 'name', string="LER name", readonly=True, type="char", size=256),
        'picking_ler': fields.char('Picking LER', size=32, readonly=True),
        'building_nif': fields.related('building_site_id', 'vat_producer', string="Producer N.I.F/C.I.F", readonly=True, type="char", size=256),
        'building_city': fields.related('building_site_id', 'city_producer', string="Council", readonly=True, type="char", size=64),
        'building_province': fields.related('building_site_id', 'province_producer', string="Province", readonly=True, type="char", size=64),
        'partner_id': fields.many2one('res.partner', "Customer", readonly=True),
        'picking_id': fields.many2one('stock.service.picking', 'Picking', readonly=True),
        'memory_include': fields.boolean('Memory include', readonly=True),
        'manager_partner_id': fields.many2one('res.partner', "Manager", readonly=True),
        'no_computed': fields.boolean('No computed'),
        'stock_picking_id': fields.many2one('stock.picking', 'Stock picking', readonly=True)
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr,  "valorization_lines")

        cr.execute("""
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
valorization_lines()
