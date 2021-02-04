# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class PriorTransferDocumentation(models.Model):

    _name = "prior.transfer.documentation"
    _description = "(NT) Prior transfer documentation"

    producer_promoter_id = fields.Many2one("res.partner", "Producer/Promoter",
                                           required=True)
    operator_partner_id = fields.\
        Many2one("res.partner", "Operator", required=True,
                 default=lambda self: self.env.user.company_id.partner_id.id)

    manager_partner_id = fields.\
        Many2one("res.partner", "Manager", required=True)
    name = fields.Char("Number", readonly=True, default="/", required=True)
    freq = fields.Selection([("DIARIA", "Diaria"), ("SEMANAL", "Semanal"),
                             ("QUINCENAL", "Quincenal"),
                             ("MENSUAL", "Mensual"),
                             ("TRIMESTRAL", "Trimestral"),
                             ("SEMESTRAL", "Semestral"), ("ANUAL", "Anual"),
                             ("OTROS", "Otros")], "Frequency", required=True,
                            default="MENSUAL")
    line_ids = fields.One2many("prior.transfer.documentation.line",
                               "nt_id", "Lines")

    @api.model
    def create(self, vals):
        if vals.get('name') == "/":
            vals['name'] = self.env["ir.sequence"].next_by_code("nt_document")
        return super().create(vals)


class PriorTransferDocumentationLine(models.Model):

    _name = "prior.transfer.documentation.line"
    _description = "(NT) Prior transfer documentation line"

    waste_id = fields.Many2one("waste.ler.code", "LER", required=True)
    nt_id = fields.Many2one("prior.transfer.documentation", "NT")
    waste_qty = fields.Float("Qty. (net Kg.)", required=True)

