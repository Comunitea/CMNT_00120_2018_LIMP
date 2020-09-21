from odoo import models, fields


class ProductsUsed(models.Model):

    _name = "products.used"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", "Product", required=True)
    treated_area = fields.Char("Treated area", required=True)
    type_of_biocide = fields.Char(
        "Type of Biocide", related="product_id.biocide_type", readonly=True
    )
    active_matter = fields.Char(
        "Active matter",
        related="product_id.active_matter_percent",
        readonly=True,
    )
    registration_number = fields.Char(
        "Registration Number",
        related="product_id.registration_no",
        readonly=True,
    )
    application_method = fields.Char(
        "Application method",
        related="product_id.application_method",
        readonly=True,
    )
    dose = fields.Char("Dose", related="product_id.dosis", readonly=True)
    picking_id = fields.Many2one("stock.service.picking", "Picking")
    security_term = fields.Char(
        "Security term", related="product_id.security_term", readonly=True
    )

    plague_to_fight = fields.Selection(
        [
            ("insects", "Insects"),
            ("microorganisms", "Microorganisms"),
            ("rodents", "Rodents"),
        ],
        "Plague to fight",
        required=True,
    )
