# -*- coding: utf-8 -*-
from odoo import models, fields

class LimpContractManualDDD(models.Model):
    _inherit = 'limp.contract'

    periodicity_desratizacion= fields.Selection([('mensual', 'Mensual'), ('bimensual', 'Bimensual'), ('trimestral', 'Trimestral'),
                            ('cuatrimestral', 'Cuatrimestral'), ('bianual', 'Bianual'), ('anual', 'Anual')], string="Periodicity desratizacion")
    periodicity_desinsectacion= fields.Selection([('mensual', 'Mensual'), ('bimensual', 'Bimensual'), ('trimestral', 'Trimestral'),
                            ('cuatrimestral', 'Cuatrimestral'), ('bianual', 'Bianual'), ('anual', 'Anual')], string="Periodicity desinsectacion")
    periodicity_desinfeccion= fields.Selection([('mensual', 'Mensual'), ('bimensual', 'Bimensual'), ('trimestral', 'Trimestral'),
                            ('cuatrimestral', 'Cuatrimestral'), ('bianual', 'Bianual'), ('anual', 'Anual')], string="Periodicity desinfeccion")

    type_ddd_ids=fields.Many2many('types.ddd', string='Types ddd')
    used_product_ids = fields.Many2many('product.product', string="Products used")


