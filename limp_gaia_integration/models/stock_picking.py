# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class StockPicking(models.Model):

    _inherit = "stock.picking"

    operator_partner_id = fields.Many2one("res.partner", "Operator",
                                          default=lambda self: self.env.user.
                                          company_id.partner_id.id)
    nt_doc_id = fields.Many2one("prior.transfer.documentation", "NT")
