# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    address_tramit_id = fields.Many2one("res.partner", "Tramit address")

    def _compute_integrations_count(self):
        for inv in self:
            inv.integration_count = len(inv.integration_ids)

    def _compute_can_integrate(self):
        for inv in self:
            for method in inv.partner_id.invoice_integration_method_ids:
                if not self.env["account.invoice.integration"].search(
                    [
                        ("invoice_id", "=", inv.id),
                        ("method_id", "=", method.id),
                    ]
                ):
                    inv.can_integrate = True
                else:
                    inv.can_integrate = False
