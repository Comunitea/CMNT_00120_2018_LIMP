# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiéira Saavedra$
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
from odoo.addons import decimal_precision as dp

class ServicePickingOtherConceptsRel(models.Model):
    _name = 'service.picking.other.concepts.rel'


    product_id = fields.Many2one('product.product', 'Product', required=True, default=1)
    name = fields.Char('Name', size=256, required=True)
    product_qty = fields.Float('Qty.', digits=(12,3), required=True)
    service_picking_id = fields.Many2one('stock.service.picking', 'Service picking')
    billable = fields.Boolean('Billable', default=True)

    @api.onchange('product_id')
    def onchange_product_id_warning(self):
        if not self.product_id:
            return
        self.name = self.product_id.name

        warning = {}
        if self.product_id.picking_warn != 'no-message':
            if self.product_id.picking_warn == 'block':
                raise UserError(self.product_id.picking_warn_msg)
            title = _("Warning for %s") % self.product_id.name
            message = self.product_id.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
            res['warning'] = warning

        return res
