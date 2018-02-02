# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class service_picking_valorization_rel(osv.osv):
    _name = 'service.picking.valorization.rel'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'name': fields.char('Name', size=128, required=True),
        'product_qty': fields.float('Qty.', digits_compute = dp.get_precision('Sale Price'), required=True),
        'service_picking_id': fields.many2one('stock.service.picking', 'Service picking'),
        'billable' : fields.boolean('Billable'),
        'memory_include': fields.boolean('Memory include'),
        'gross_weight': fields.float('Gross (T.)', digits=(12,3), help="Gross weight in T"),
        'tare': fields.float('Tare (T.)', digits=(12,3), help="Tare in T."),
        'net_weight': fields.float('Net (T.)', digits=(12,3), help="Net weight in T."),
        'overload_qty': fields.float('Overload', digits=(12,2), help="Overload in m³"),
        'volume': fields.float('Volume (m³)', digits=(12,2), help="Volume in m³"),
        'ler_code': fields.char('Ler', size=20),
        'no_compute': fields.boolean('No compute'),
        'delegation_id': fields.many2one('hr.department', 'Department', change_default=True),
        'company_id': fields.many2one('res.company', 'Company', change_default=True)
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: context.get('company_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id and self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id or False,

    }

    def onchange_product_id_warning(self,cr,uid,ids,product_id=False, manager_partner_id=False):
        res = {}
        if not product_id:
            return res
        product_obj = self.pool.get('product.product').browse(cr, uid, product_id)

        res['value'] = {'name': product_obj.name}
        if product_obj.ler_code_id:
            res['value']['ler_code'] = product_obj.ler_code_id.code

        if manager_partner_id:
            company_ids = self.pool.get('res.company').search(cr, 1, [])
            partner_data = self.pool.get('res.company').read(cr, 1, company_ids, ['partner_id'])
            partner_ids = [x['partner_id'][0] for x in partner_data]
            if manager_partner_id not in partner_ids:
                res['value']['memory_include'] = False
            else:
                res['value']['memory_include'] = True

        warning = {}
        if product_obj.picking_warn != 'no-message':
            if product_obj.picking_warn == 'block':
                raise osv.except_osv(_('Alert for %s !') % (product_obj.name), product_obj.picking_warn_msg)
            title = _("Warning for %s") % product_obj.name
            message = product_obj.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
            res['warning'] = warning

        return res

    def onchange_net_weight(self, cr, uid, ids, net_weight=0.0, product_id=False, no_compute=False):
        res = {}
        if no_compute or not product_id:
            return res

        product = self.pool.get('product.product').browse(cr, uid, product_id)
        if product.uos_coeff:
            res['value'] = {
                'product_qty': round(net_weight / product.uos_coeff, 2),
                'volume': round(net_weight / product.uos_coeff, 2)
            }

        return res

    def onchange_volume(self, cr, uid, ids, qty=0.0, product_id=False, no_compute=False):
        res = {}
        if no_compute or not product_id:
            return res

        product = self.pool.get('product.product').browse(cr, uid, product_id)
        res['value'] = {
            'product_qty': qty,
            'volume': qty
        }

        if product.uos_coeff:
            res['value']['net_weight'] = round(qty * product.uos_coeff, 2)

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        if vals.get('memory_include', False):
            user = self.pool.get('res.users').browse(cr, uid, uid)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'limp_service_picking', 'group_waste_memory')
            res_id = res and res[1] or False
            if res_id:
                user_groups = [x.id for x in user.groups_id]
                if res_id not in user_groups:
                    vals['memory_include'] = False

        return super(service_picking_valorization_rel, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if vals.get('memory_include', False):
            user = self.pool.get('res.users').browse(cr, uid, uid)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'limp_service_picking', 'group_waste_memory')
            res_id = res and res[1] or False
            if res_id:
                user_groups = [x.id for x in user.groups_id]
                if res_id not in user_groups:
                    vals['memory_include'] = False

        return super(service_picking_valorization_rel, self).write(cr, uid, ids, vals, context=context)

service_picking_valorization_rel()
