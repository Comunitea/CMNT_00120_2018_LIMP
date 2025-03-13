from odoo import models, fields


class ExtinguisherBiesAnomalies(models.Model):
    _name = "extinguisher.bies.anomalies"
    _description = "Extinguisher Bies Anomalies"

    name = fields.Char("Name")
    picking_id = fields.Many2one("stock.service.picking", "Picking")
    date = fields.Date("Date")
    contract_id = fields.Many2one("limp.contract", "Contract")
