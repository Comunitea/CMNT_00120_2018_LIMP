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
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ServicePickingInvoiceConcept(models.Model):

    _order = "sequence asc"

    _name = 'service.picking.invoice.concept'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    name = fields.Char('Name', size=256, required=True)
    price = fields.Float('Price', digits=(12,2))
    notes = fields.Text('Notes')
    product_qty = fields.Float('Qty.', digits=(12,3))
    product_uom = fields.Many2one('product.uom', 'Product uom')
    service_picking_id = fields.Many2one('stock.service.picking', 'Service picking')
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal')
    tax_ids = fields.Many2many('account.tax', 'invoice_concept_tax_rel', 'concept_line_ids', 'tax_ids', 'Taxes')
    taxes_str = fields.Text('Taxes', compute='_compute_taxes_str')
    sequence = fields.Integer('Seq.', default=1)

    @api.depends('tax_ids')
    def _compute_taxes_str(self):
        for obj in self:
            if obj.tax_ids:
                obj.taxes_str = u", ".join([x.name for x in obj.tax_ids])
            else:
                obj.taxes_str = ""

    @api.depends('product_qty', 'price')
    def _compute_subtotal(self):
        for obj in self:
            obj.subtotal = obj.product_qty * obj.price

    @api.onchange('product_id')
    def product_id_change(self):
        warning = {}
        if self.product_id:
            product_obj = self.product_id
            result['notes'] = product_obj.description
            result['product_uom'] = product_obj.uom_id.id
            fpos = product_obj.service_picking_id.fiscal_position
            result['tax_ids'] = fpos.map_tax(product_obj.taxes_id)
            result['price'] = product_obj.list_price

            if product_obj.picking_warn != 'no-message':
                if product_obj.picking_warn == 'block':
                    raise UserError(product_obj.picking_warn_msg)
                title = _("Warning for %s") % product_obj.name
                message = product_obj.picking_warn_msg
                warning['title'] = title
                warning['message'] = message
        return {'warning':warning}

    def _amount_line_tax(self):
        self.ensure_one()
        val = 0.0
        for c in self.tax_ids.compute_all(self.price, quantity=self.product_qty, product=self.product_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
