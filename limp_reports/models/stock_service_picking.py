# © 2026 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import locale
import uuid

from odoo import fields, models


class StockServicePicking(models.Model):
    _inherit = "stock.service.picking"

    access_token = fields.Char(
        string="Token de acceso",
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )
    qr_download_image = fields.Binary(
        string="QR descarga albarán",
        compute="_compute_qr_download_image",
    )

    def _get_service_picking_share_url(self):
        """Public url to download the PDF picking (albarán) without login."""
        self.ensure_one()
        if not self.access_token:
            self.access_token = str(uuid.uuid4())
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return "%s/limp/service_picking/%s/download?access_token=%s" % (
            base_url,
            self.id,
            self.access_token,
        )

    def _compute_qr_download_image(self):
        report_obj = self.env["ir.actions.report"]
        for picking in self:
            url = picking._get_service_picking_share_url()
            qr_png = report_obj.barcode("QR", url, width=300, height=300)
            picking.qr_download_image = base64.b64encode(qr_png)

    def _cert_envio_gestor_externo_today(self):
        """Spanish long formatted date (e.g. '30 de noviembre de 2025') for the report letterhead."""
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        return fields.Date.context_today(self).strftime("%d de %B de %Y")

    def _cert_envio_gestor_externo_partner_address(self, partner):
        """Plain 'street, zip city' address, without the partner name (unlike contact_address)."""
        parts = [part for part in (partner.street, partner.street2) if part]
        city_parts = [part for part in (partner.zip, partner.city) if part]
        if city_parts:
            parts.append(" ".join(city_parts))
        return ", ".join(parts)
