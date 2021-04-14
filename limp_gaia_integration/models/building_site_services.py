# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class BuildingSiteServices(models.Model):
    _inherit = "building.site.services"

    producer_promoter_id = fields.Many2one("res.partner", "Producer/Promoter")

    @api.onchange('producer_promoter_id')
    def onchage_producer_promoter_id(self):
        if self.producer_promoter_id:
            self.producer_promoter = self.producer_promoter_id.\
                commercial_partner_id.name
            self.address_producer = self.producer_promoter_id.street
            self.vat_producer = self.producer_promoter_id.vat
            self.city_producer = self.producer_promoter_id.city
            self.province_producer = self.producer_promoter_id.state_id.name
