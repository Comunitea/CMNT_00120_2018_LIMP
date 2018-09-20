# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DetectedSpecies(models.Model):

    _name = 'detected.species'

    name=fields.Selection([('insects', 'Insects'),('microorganisms', 'Microorganisms'),('rodents', 'Rodents')],'Name', required=True)
    location=fields.Char('Location')
    level_mild=fields.Boolean('Mild')
    level_medium=fields.Boolean('Medium')
    level_high=fields.Boolean('High')


    @api.onchange('level_mild')
    def on_change_level_mild(self):

        if self.level_mild:
            self.level_medium=False
            self.level_high=False

    @api.onchange('level_medium')
    def on_change_level_medium(self):

        if self.level_medium:
            self.level_mild=False
            self.level_high=False

    @api.onchange('level_high')
    def on_change_level_high(self):

        if self.level_high:
            self.level_mild=False
            self.level_medium=False
