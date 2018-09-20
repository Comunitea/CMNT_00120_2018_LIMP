# -*- coding: utf-8 -*-
from odoo import models, fields

class LimpContractManualDDD(models.Model):
    _inherit = 'limp.contract'

    periodicity_reviews = fields.Selection([('mensual', 'mensual'), ('bimensual', 'bimensual'), ('trimestral', 'trimestral'), ('cuatrimestral', 'cuatrimestral'), ('bianual', 'bianual'), ('anual', 'anual')], string="Periodicity Reviews")

    type_ddd_ids=fields.Many2many('types.ddd', string='Types ddd')

    technical_team=fields.Many2many('hr.employee', string='Technical Team')


