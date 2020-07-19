from odoo import models, fields


class ObservationRecommendationDDD(models.Model):

    _name = "observation.recommendation.ddd"

    name = fields.Char("Measures to be taken")
    observation = fields.Char("Observations")
