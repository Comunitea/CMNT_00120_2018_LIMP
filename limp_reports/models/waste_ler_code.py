from odoo import models, fields


class WasteLerCode(models.Model):
    _inherit = 'waste.ler.code'

    valorization_percentage = fields.Float('Valorization percentage')
