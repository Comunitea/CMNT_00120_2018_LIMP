# Copyright 2021 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Limpergal Gaia Integration",
    "description": "Integrates waste service pickings with Gaia.",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "website": "https://www.comunitea.com",
    "category": "Integrations",
    "depends": [
        "limp_service_picking",
        "city_council",
        "base_iso3166",
        "l10n_es_cnae",
        "limp_reports",
        "report_xml"
    ],
    "data": ["data/limp_gaia_integration_data.xml",
             "security/ir.model.access.csv",
             "views/stock_service_picking_view.xml",
             "views/stock_picking_view.xml",
             "views/res_partner_view.xml",
             "views/building_site_service_view.xml",
             "views/prior_transfer_documentation_view.xml",
             "views/report_di.xml",
             "views/waste_ler_code_view.xml",
             "views/report_nt.xml",
             "report/stock_service_picking_di_report.xml",
             "report/stock_picking_di_report.xml",
             "report/prior_transfer_documentation_report.xml"],
    "installable": True,
}
