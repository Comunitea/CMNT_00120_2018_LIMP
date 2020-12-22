# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountAnalyticTag(models.Model):

    _inherit = "account.analytic.tag"
    _order = "sequence asc"

    show_in_report = fields.Boolean()
    sequence = fields.Integer()


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    journal_tag_id = fields.Many2one(
        "account.analytic.tag",
        "Journal",
        compute="_compute_journal_id",
        store=True,
    )

    @api.multi
    @api.depends("tag_ids")
    def _compute_journal_id(self):
        for line in self:
            tags = line.tag_ids.filtered("show_in_report")
            line.journal_tag_id = tags and tags[0].id or False
