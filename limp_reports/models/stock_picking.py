# © 2026 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import locale
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

    def _cert_recepcion_today(self):
        """Spanish long formatted date (e.g. '30 de noviembre de 2025') for the report letterhead."""
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        return fields.Date.context_today(self).strftime("%d de %B de %Y")

    def _cert_recepcion_partner_address(self, partner):
        """Plain 'street, zip city' address, without the partner name (unlike contact_address)."""
        parts = [part for part in (partner.street, partner.street2) if part]
        city_parts = [part for part in (partner.zip, partner.city) if part]
        if city_parts:
            parts.append(" ".join(city_parts))
        return ", ".join(parts)

    def _cert_recepcion_authorization_no(self, ler_code):
        """Own company treatment ('E0x') authorization number for the given LER code."""
        ler_code_id = self.env["waste.ler.code"].search([("code", "=", ler_code)], limit=1)
        authorization = self.company_id.partner_id.ler_authorization_ids.filtered(
            lambda auth: ler_code_id in auth.ler_code_ids
            and str(auth.authorization_type).startswith("E")
        )
        return authorization[0].name if authorization else ""
