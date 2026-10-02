# © 2026 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import uuid

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    access_token = fields.Char(
        string="Token de acceso",
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )
    outgoing_report_qr_image = fields.Binary(
        string="QR descarga xustificante",
        compute="_compute_outgoing_report_qr_image",
    )

    def _get_outgoing_report_share_url(self):
        """Public url to download the outgoing report PDF without login."""
        self.ensure_one()
        if not self.access_token:
            self.access_token = str(uuid.uuid4())
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return "%s/limp/outgoing_report/%s/download?access_token=%s" % (
            base_url,
            self.id,
            self.access_token,
        )

    def _compute_outgoing_report_qr_image(self):
        report_obj = self.env["ir.actions.report"]
        for picking in self:
            url = picking._get_outgoing_report_share_url()
            qr_png = report_obj.barcode("QR", url, width=300, height=300)
            picking.outgoing_report_qr_image = base64.b64encode(qr_png)
