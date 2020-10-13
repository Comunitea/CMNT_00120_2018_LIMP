##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class LimpServicePicking(models.Model):
    _inherit = "stock.service.picking"

    sale_line_ids = fields.One2many(
        "sale.order.line", related="sale_id.order_line", readonly=True
    )


class ServicePickingOtherConceptsRel(models.Model):
    _inherit = "service.picking.other.concepts.rel"

    price_unit = fields.Float(
        "Price Unit", digits=dp.get_precision("Sale Price")
    )

    @api.onchange("product_id")
    def onchange_product_id_warning(self):
        res = super().onchange_product_id_warning()
        if self.service_picking_id and self.product_id:
            lines = self.service_picking_id.sale_line_ids
            use_line = lines.filtered(
                lambda r: r.product_id == self.product_id
            )
            if use_line:
                self.price_unit = use_line[0].price_unit
                self.name = use_line[0].name
            elif self.service_picking_id.pricelist_id:
                product_context = \
                    dict(self.env.context,
                         partner_id=self.service_picking_id.partner_id.id,
                         date=self.service_picking_id.retired_date or
                         self.service_picking_id.picking_date,
                         uom=self.product_id.uom_id.id)
                final_price, rule_id = self.service_picking_id.pricelist_id.\
                    with_context(product_context).\
                    get_product_price_rule(self.product_id,
                                           self.product_qty,
                                           self.service_picking_id.partner_id)
                self.price_unit = final_price
            else:
                self.price_unit = self.product_id.lst_price
        return res
