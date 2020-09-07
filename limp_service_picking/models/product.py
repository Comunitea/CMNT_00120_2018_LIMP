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
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = "product.template"

    ler_code_id = fields.Many2one("waste.ler.code", "LER")
    overload_price = fields.Float(
        "Overload price", digits=dp.get_precision("Sale Price")
    )
    tax_product = fields.Boolean("Tax product", readonly=False,
                                 related="product_variant_ids.tax_product")
    biocide_type = fields.Char("Biocide type", size=150, readonly=False,
                               related="product_variant_ids.biocide_type")
    active_matter_percent = fields.\
        Float("Active Mater (%)", digits=(16, 3), readonly=False,
              related="product_variant_ids.active_matter_percent")
    registration_no = fields.\
        Char("Registration no.", size=150, readonly=False,
             related="product_variant_ids.registration_no")
    application_method = fields.\
        Char("Application method", size=150, readonly=False,
             related="product_variant_ids.application_method")
    dosis = fields.Float("Dosis (%)", digits=(16, 3), readonly=False,
                         related="product_variant_ids.dosis")
    security_term = fields.Char("Security term", size=150, readonly=False,
                                related="product_variant_ids.security_term")


class ProductProduct(models.Model):
    _inherit = "product.product"

    tax_product = fields.Boolean("Tax product")
    biocide_type = fields.Char("Biocide type", size=150)
    active_matter_percent = fields.Float("Active Mater (%)", digits=(16, 3))
    registration_no = fields.Char("Registration no.", size=150)
    application_method = fields.Char("Application method", size=150)
    dosis = fields.Float("Dosis (%)", digits=(16, 3))
    security_term = fields.Char("Security term", size=150)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        for arg in args:
            if isinstance(arg, list) and "in" in arg[1]:
                ids = []
                change = False
                for elem in arg[2]:
                    if isinstance(elem, list) and len(elem) == 3 and elem[1]:
                        change = True
                        ids.append(elem[1])
                    elif (
                        isinstance(elem, list)
                        and len(elem) == 3
                        and not elem[1]
                        and isinstance(elem[2], list)
                    ):
                        change = True
                        ids.extend(elem[2])
                if change:
                    arg[2] = ids
        return super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        for arg in args:
            if isinstance(arg, list) and "in" in arg[1]:
                ids = []
                change = False
                for elem in arg[2]:
                    if isinstance(elem, list) and len(elem) == 3 and elem[1]:
                        change = True
                        ids.append(elem[1])
                    elif (
                        isinstance(elem, list)
                        and len(elem) == 3
                        and not elem[1]
                        and isinstance(elem[2], list)
                    ):
                        change = True
                        ids.extend(elem[2])
                if change:
                    arg[2] = ids
        return super(ProductProduct, self).search(
            args, offset, limit, order, count=count
        )
