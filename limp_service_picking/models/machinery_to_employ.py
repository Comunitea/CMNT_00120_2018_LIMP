# -*- coding: utf-8 -*-
from odoo import models, fields

class MachineryToEmploy(models.Model):

    _name = 'machinery.to.employ'

    name=fields.Char("Equipment", required=True)
    purpose_machinery=fields.Text("Purpose machinery")
