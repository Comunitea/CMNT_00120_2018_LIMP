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

    @api.multi
    def open_treatment_contract_docs(self):
        self.ensure_one()
        form_view_id = self.env.ref("limp_reports.acceptance_doc_form")
        tree_view_id = self.env.ref("limp_reports.acceptance_doc_tree")

        return {
            "name": "CTs",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "acceptance.document",
            "domain": "[('building_site_id', '=', [{0}])]".format(self.id),
            "context": "{'default_building_site_id': %s}" % self.id,
            "view_id": tree_view_id.id,
            "views": [(tree_view_id.id, "tree"), (form_view_id.id, "form")],
            "type": "ir.actions.act_window",
            "nodestroy": True,
        }
