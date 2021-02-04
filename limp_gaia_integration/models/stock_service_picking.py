# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockServicePicking(models.Model):

    _inherit = "stock.service.picking"

    operator_partner_id = fields.Many2one(
        "res.partner",
        "Operator",
        states={
            "closed": [("readonly", True)],
            "cancelled": [("readonly", True)],
        },
        default=lambda self: self.env.user.company_id.partner_id.id
    )
    nt_doc_id = fields.Many2one("prior.transfer.documentation", "NT")
    producer_promoter_id = fields.Many2one("res.partner", "Producer/Promoter")
    holder_builder_id = fields.Many2one("res.partner", "Holder/Builder")

    @api.onchange("building_site_id")
    def onchange_building_site_id(self):
        if self.building_site_id:
            if self.building_site_id:
                self.producer_promoter_id = \
                    self.building_site_id.producer_promoter_id.id
                self.holder_builder_id = \
                    self.building_site_id.holder_builder_id.id

        super().onchange_building_site_id()
