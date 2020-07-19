# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, exceptions, _


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    analytic_target_ids = fields.One2many(
        "account.analytic.target", "analytic_tag_id", "Targets"
    )
