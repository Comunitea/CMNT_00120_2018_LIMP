# © 2026 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class ServicePickingPublicDownload(http.Controller):

    def _render_jasper_pdf_response(self, report_name, record):
        report = (
            request.env["ir.actions.report"]
            .sudo()
            .search(
                [
                    ("report_name", "=", report_name),
                    ("report_file", "ilike", ".jrxml"),
                ],
                limit=1,
            )
        )
        pdf_content, _report_format = report.render_jasper(record.ids, {})
        return request.make_response(
            pdf_content,
            headers=[
                ("Content-Type", "application/pdf"),
                (
                    "Content-Disposition",
                    'attachment; filename="%s.pdf"' % (record.name or "albaran"),
                ),
            ],
        )

    @http.route(
        "/limp/service_picking/<int:picking_id>/download",
        type="http",
        auth="public",
    )
    def download_service_picking(self, picking_id, access_token=None, **kwargs):
        picking = request.env["stock.service.picking"].sudo().browse(picking_id)

        if (
            not picking.exists()
            or not access_token
            or picking.access_token != access_token
        ):
            return request.make_response("Not Found", status=404)

        return self._render_jasper_pdf_response("service_picking", picking)

    @http.route(
        "/limp/outgoing_report/<int:picking_id>/download",
        type="http",
        auth="public",
    )
    def download_outgoing_report(self, picking_id, access_token=None, **kwargs):
        picking = request.env["stock.picking"].sudo().browse(picking_id)

        if (
            not picking.exists()
            or not access_token
            or picking.access_token != access_token
        ):
            return request.make_response("Not Found", status=404)

        return self._render_jasper_pdf_response("outgoing_report", picking)
