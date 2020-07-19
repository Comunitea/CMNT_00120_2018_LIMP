# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountAnalyticDistribution(models.Model):

    _inherit = "account.analytic.distribution"

    tag_id = fields.Many2one("account.analytic.tag", "Tag")
