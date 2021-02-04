# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResPartnerLerAuthorization(models.Model):

    _name = "res.partner.ler.authorization"
    _description = "Partner LER Authorization"

    name = fields.Char("Authorizatio no.", required=True)
    partner_id = fields.Many2one("res.partner", "Manager", required=True)
    ler_code_ids = fields.Many2many("waste.ler.code", string="Related LERs",
                                    required=True)
