from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    valorization_percentage = fields.Float('Valorization percentage')
