# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

from openerp import models, fields
from tools.translate import _
import netsvc

class stock_picking(models.Model):
    _inherit = "stock.picking"
    _columns = {
        'stock_service_picking_id': fields.many2one('stock.service.picking','Stock service picking'),
        'from_spicking' : fields.boolean("From service picking", readonly=True),
        'invoice_type': fields.selection([('out_invoice','Out invoice'),('in_invoice', 'In invoice')], 'Invoice type'),
        'memory_include': fields.boolean('Include in annual memory'),
        'waste_or_arid': fields.selection([('waste', 'Wastes'), ('arid', 'Arid')], 'Waste/Arid'),
        'manager_or_productor': fields.selection([('manager', 'Manager'), ('productor', 'Productor')], 'Manager/Productor'),
        'carrier_id': fields.many2one('res.partner', 'Carrier'),
        'license_plate': fields.char('License plate', size=18),
        'driver_id': fields.many2one('hr.employee', 'Driver'),
        'delivery_kms': fields.integer('Delivery kms.'),
        'arrival_kms': fields.integer('Arrival kms.'),
        'delivery_hours': fields.float('Delivery hours', digits=(4,2)),
        'displacement_hours': fields.float('Displacement hours', digits=(4,2)),
        'work_hours': fields.float('Work hours', digits=(4,2)),
        'tranfer_hours': fields.float('Transfer hours', digits=(4,2)),
        'arrival_hours': fields.float('Arrival hours', digits=(4,2)),
    }

    _defaults = {
        'manager_or_productor': 'productor',
        'waste_or_arid': 'waste',
        'delivery_kms': 0.0,
        'arrival_kms': 0.0,
        'delivery_hours': 0.0,
        'displacement_hours': 0.0,
        'work_hours': 0.0,
        'tranfer_hours': 0.0,
        'arrival_hours': 0.0,
    }

    def _get_invoice_type(self, pick):

        inv_type = super(stock_picking, self)._get_invoice_type(pick)

        if pick.invoice_state == '2binvoiced' and pick.from_spicking and pick.type == 'in':
            return 'out_invoice'
        elif pick.invoice_type:
            return pick.invoice_type
        else:
            return inv_type

    def _get_price_unit_invoice(self, cr, uid, move_line, type):
        res = super(stock_picking, self)._get_price_unit_invoice(cr, uid, move_line, type)
        if (not move_line.sale_line_id and not move_line.purchase_line_id) and move_line.picking_id.partner_id:
            if 'in_' in type:
                pricelist_id = move_line.picking_id.partner_id.property_product_pricelist_purchase
            else:
                pricelist_id = move_line.picking_id.partner_id.property_product_pricelist

            if pricelist_id:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id.id],
                    move_line.product_id.id, move_line.product_qty or 1.0, move_line.picking_id.partner_id, {
                        'uom': move_line.product_uom.id,
                        'date': move_line.picking_id.date or False,
                        })[pricelist_id.id]

                return price

        return res

    def force_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if moves are confirmed or waiting.
        @return: True
        """
        reserve_moves = []
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            move_ids = [x.id for x in pick.move_lines if x.state in ['confirmed','waiting']]
            user = self.pool.get('res.users').browse(cr, uid, uid)
            visited_products = []
            for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
                if move.product_id.ler_code_id and pick.type == 'out':
                    orig_qty = move.product_id.virtual_available
                    if orig_qty < 0.0 and move.product_id.id not in visited_products:
                        visited_products.append(move.product_id.id)
                        if not user.company_id.reserve_product_id:
                            raise osv.except_osv(_(u'Error !'), _(u'You have not enough quantity to serve the product %s. Then you have to set teh reserve product in company for using it.') % (move.product_id.name,))
                        else:
                            if user.company_id.reserve_product_id.uom_id.category_id.id == move.product_id.uom_id.category_id.id:
                                qty = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, -(orig_qty), user.company_id.reserve_product_id.uom_id.id)
                            else:
                                qty = -orig_qty / move.product_id.ler_code_id.density

                            #movimiento de consumo del producto resevado, de Stock a producción
                            move_vals = {
                                'name': u"Used to serve %s in picking %s" % (move.product_id.name,pick.name),
                                'product_id': user.company_id.reserve_product_id.id,
                                'product_qty': qty,
                                'product_uom': user.company_id.reserve_product_id.uom_id.id,
                                'location_id': move.location_id.id,
                                'location_dest_id': user.company_id.reserve_product_id.property_stock_production.id
                            }
                            reserve_moves.append(self.pool.get('stock.move').create(cr, uid, move_vals))
                            #movimiento de creación del producto a enviar
                            move_vals2 = {
                                'name': "Created from reserve product",
                                'product_id': move.product_id.id,
                                'product_qty': -(orig_qty),
                                'product_uom': move.product_id.uom_id.id,
                                'location_id': move.product_id.property_stock_production.id,
                                'location_dest_id': move.location_id.id
                            }
                            reserve_moves.append(self.pool.get('stock.move').create(cr, uid, move_vals2))

            if reserve_moves:
                self.pool.get('stock.move').action_confirm(cr, uid, reserve_moves)
                self.pool.get('stock.move').force_assign(cr, uid, reserve_moves)
                picking_vals = {
                    'origin': pick.name,
                    'type': 'internal',
                    'move_lines': [(6, 0, reserve_moves)]
                }
                pick_id = self.create(cr, uid, picking_vals)
                wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_confirm', cr)
                self.action_move(cr, uid, [pick_id])
                wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_done', cr)

        return super(stock_picking, self).force_assign(cr, uid, ids, args)

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        self.pool.get('account.invoice.line').write(cr, uid, [invoice_line_id], {'move_id': move_line.id})
        res = super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)
        if move_line.description:
            self.pool.get('account.invoice.line').write(cr, uid, [invoice_line_id], {'name': move_line.description})

        return res

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        res = super(stock_picking, self)._invoice_hook(cr, uid, picking,
                                                       invoice_id)
        if picking.from_spicking:
            invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
            def_analytic_ids = self.pool.get('account.analytic.default').search(cr, uid, [("inv_type", "=", invoice.type)])
            if def_analytic_ids:
                def_analytic_id = self.pool.get('account.analytic.default').browse(cr, uid, def_analytic_ids[0])
                self.pool.get('account.invoice').write(cr, uid, [invoice_id], {"analytic_id": def_analytic_id.analytic_id.id})
        return res

stock_picking()
