# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductsUsed(models.Model):

    _name = 'products.used'

    name=fields.Char("Tradename", required=True)
    treated_area=fields.Char("Treated area")
    type_of_biocide=fields.Char("Type of Biocide")
    active_matter=fields.Char("Active matter")
    registration_number=fields.Char("Registration Number")
    application_method= fields.Char("Application method")
    dose=fields.Char("Dose")
    security_term=fields.Char("Security term")
