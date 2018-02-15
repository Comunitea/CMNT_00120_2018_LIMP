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

"""Model to register containers"""

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp
import time

class Container(models.Model):
    """Model to register containers"""

    _name = "container"
    _description = "Containers"
    _rec_name = "code"

    code = fields.Char('Code', size=10, readonly=True)
    type = fields.Selection([('flat_dumpster15', 'Flat Dumpster 1,5'), ('flat_dumpster3', 'Flat Dumpster 3'), ('flat_dumpster4', 'Flat Dumpster 4'), ('flat_dumpster7', 'Flat Dumpster 7'), ('flat_dumpster9', 'Flat Dumpster 9'), ('flat_dumpster12', 'Flat Dumpster 12'),
                    ('flat_dumpster14', 'Flat Dumpster 14'), ('flat_dumpster18', 'Flat Dumpster 18'), ('flat_dumpster30', 'Flat Dumpster 30'), ('trapezoidal4', 'Trapezoidal 4'), ('trapezoidal6', 'Trapezoidal 6'),
                    ('trapezoidal8', 'Trapezoidal 8'), ('other', 'Other')], 'Type', required=True, default='flat_dumpster9')
    shape = fields.Selection([('opened', 'Opened'),('closed', 'Closed')], 'Shape', required=True, default='opened')
    dimensions = fields.Char('Dimensions', size=32)
    capacity = fields.Float('Capacity (m³)', digits=dp.get_precision('Product UoM'))
    note = fields.Text('Observations')
    active = fields.Boolean('Active', default=True)
    history_ids = fields.One2many('container.move', 'container_id', 'History', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda r: r.env.user.company_id.id)
    last_move_date = fields.Datetime('Last move date', readonly=True)
    last_responsible_id = fields.Many2one('hr.employee', 'Last driver', readonly=True)
    #'product_id': fields.many2one('product.product', 'Product', required=True),
    #'product_tmpl_id': fields.related('product_id', 'product_tmpl_id', type="many2one", relation="product.template", string="Product template", readonly=True),
    #'amount': fields.related('product_tmpl_id','list_price',string='Amount', digits_compute=dp.get_precision('Account'), readonly=True, type="float"),
    situation_id = fields.Many2one('res.partner', 'Situation', help="Current situation, customer address or available in company addresses", default=lambda r: r.env.user.company_id.partner_id.address_get()['default'])
    partner_id = fields.Many2one('res.partner', 'Partner', related='situation_id.commercial_partner_id')
    home = fields.Boolean('Home', related='situation_id.containers_store')
    container_placement = fields.Selection([('on_street', 'On street'),('on_building', 'On building')], string="Container placement")

    @api.multi
    def write(self, vals):
        """creates the registry in the history"""
        return super(Container, self).write(vals)
        '''MIGRACION: Solo firma
        if context is None: context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        if vals.get('situation_id', False) and not context.get('no_create_moves', False):
            for container_obj in self.browse(cr, uid, ids):
                if not container_obj.situation_id:
                    self.pool.get('container.move').create(cr, uid, {
                                                            'container_id': container_obj.id,
                                                            'move_type': 'out',
                                                            'address_id': vals['situation_id'],
                                                            'move_date': vals.get('last_move_date', time.strftime("%Y-%m-%d %H:%M:%S")),
                                                            'responsible_id': vals.get('last_responsible_id', False)
                                                        })
                elif vals['situation_id'] != container_obj.situation_id.id:
                    self.pool.get('container.move').create(cr, uid, {
                                                            'container_id': container_obj.id,
                                                            'move_type': 'out',
                                                            'address_id': container_obj.situation_id.id,
                                                            'move_date': vals.get('last_move_date', time.strftime("%Y-%m-%d %H:%M:%S")),
                                                            'responsible_id': vals.get('last_responsible_id', False)
                                                        })
                    self.pool.get('container.move').create(cr, uid, {
                                                            'container_id': container_obj.id,
                                                            'move_type': 'in',
                                                            'address_id': vals['situation_id'],
                                                            'move_date': vals.get('last_move_date', time.strftime("%Y-%m-%d %H:%M:%S")),
                                                            'responsible_id': vals.get('last_responsible_id', False)
                                                        })

        return super(container, self).write(cr, uid, ids, vals, context=context)'''

    @api.model
    def create(self, vals):
        '''MIGRACION: Solo firma
        sequence = ''
        if vals.get('type', False):
            if 'flat_dumpster' in vals['type']:
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'container_flat_dumpster' + vals['type'].split('flat_dumpster')[1])
            elif 'trapezoidal' in vals['type']:
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'container_trapezoidal' + vals['type'].split('trapezoidal')[1])
            elif vals['type'] == 'other':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'container_other')

        if sequence:
            vals['code'] = sequence'''
        return super(Container, self).create(vals)
