# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    council_id = fields.Many2one("city.council", "Council")
    region_id = fields.Many2one('res.country.region', 'Region',
                                domain="[('country_id', '=', country_id)]")

    @api.onchange("zip_id")
    def onchange_zip_id_set_council(self):
        if self.zip_id:
            self.council_id = self.zip_id.city_id.council_id

    @api.onchange("state_id")
    def onchange_state_id_set_region(self):
        if self.state_id:
            self.region_id = self.state_id.region_id
