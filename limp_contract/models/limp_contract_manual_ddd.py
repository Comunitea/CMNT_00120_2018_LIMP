from odoo import models, fields


class LimpContractManualDDD(models.Model):
    _inherit = "limp.contract"

    periodicity_desratizacion = fields.Selection(
        [
            ("mensual", "Mensual"),
            ("bimensual", "Bimensual"),
            ("trimestral", "Trimestral"),
            ("cuatrimestral", "Cuatrimestral"),
            ("bianual", "Bianual"),
            ("anual", "Anual"),
        ],
        string="Periodicity desratizacion",
    )
    periodicity_desinsectacion = fields.Selection(
        [
            ("mensual", "Mensual"),
            ("bimensual", "Bimensual"),
            ("trimestral", "Trimestral"),
            ("cuatrimestral", "Cuatrimestral"),
            ("bianual", "Bianual"),
            ("anual", "Anual"),
        ],
        string="Periodicity desinsectacion",
    )
    periodicity_desinfeccion = fields.Selection(
        [
            ("mensual", "Mensual"),
            ("bimensual", "Bimensual"),
            ("trimestral", "Trimestral"),
            ("cuatrimestral", "Cuatrimestral"),
            ("bianual", "Bianual"),
            ("anual", "Anual"),
        ],
        string="Periodicity desinfeccion",
    )
    periodicity_legionella = fields.Selection(
        [
            ("mensual", "Mensual"),
            ("bimensual", "Bimensual"),
            ("trimestral", "Trimestral"),
            ("cuatrimestral", "Cuatrimestral"),
            ("bianual", "Bianual"),
            ("anual", "Anual"),
        ],
        string="Periodicity legionella",
    )

    type_ddd_ids = fields.Many2many("types.ddd", string="Types ddd")
    used_product_ids = fields.Many2many(
        "product.product", string="Products used"
    )
    type_of_installation_ids = fields.Many2many(
        "type.of.installation.legionella",
        string="Types of installation legionella",
    )
