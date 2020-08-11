# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    delegation_id = fields.Many2one(
        "res.delegation",
        "Delegation",
        default=lambda r: r.env.user.context_delegation_id.id,
        index=True
    )
