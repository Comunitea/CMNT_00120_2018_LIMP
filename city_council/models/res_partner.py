# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    council_id = fields.Many2one('city.council', 'Council')

    @api.onchange('zip_id')
    def onchange_zip_id_set_council(self):
        if self.zip_id:
            self.council_id = self.zip_id.council_id
