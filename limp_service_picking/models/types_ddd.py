from odoo import models, fields, api


class TypesDDD(models.Model):

    _name = "types.ddd"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    vectors_to_fight = fields.Char()
    machinery_to_employ_ids = fields.Many2many(
        "machinery.to.employ", string="Machinery to deploy"
    )
    equipment_to_be_used_ids = fields.Many2many(
        "equipment.to.be.used", string="Equipment to employ"
    )
    observation_recommendation = fields.Many2many(
        "observation.recommendation.ddd",
        string="Observation / Recommendation ",
    )
    service_type = fields.Selection(
        [("ddd", "DDD"), ("legionella", "Legionella")], "Type", required=True
    )
