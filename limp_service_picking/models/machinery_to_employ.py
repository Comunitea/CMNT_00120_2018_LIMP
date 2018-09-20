# -*- coding: utf-8 -*-
from odoo import models, fields

class MachineryToEmploy(models.Model):

    _name = 'machinery.to.employ'

    name=fields.Char("Equipment")
    purpose_machinery=fields.Text("Purpose machinery")
    types_ddd_id = fields.Many2one("Types DDD")
