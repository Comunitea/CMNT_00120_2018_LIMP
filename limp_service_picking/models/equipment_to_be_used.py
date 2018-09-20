# -*- coding: utf-8 -*-
from odoo import models, fields

class EquipmentToBeUsed(models.Model):

    _name = 'equipment.to.be.used'

    name=fields.Char("Equipment")
    purpose_equipment=fields.Text("Purpose Equipment")
    types_ddd_id = fields.Many2one('types.ddd', string="Types DDD")
