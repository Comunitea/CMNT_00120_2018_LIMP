# -*- coding: utf-8 -*-
from odoo import models, fields

class LegionellaSamples(models.Model):

    _name = 'legionella.samples'

    name=fields.Char(required=True)
    registration_number=fields.Char('Registration Number', required=True)
    type_product=fields.Selection([('acs_acu', 'ACS accumulator'),('acs_inter_terminal', 'ACS intermediate terminal point'),('acs_far_term', 'ACS far terminal'),
    ('cold_w_cistern', 'Cold water cistern'),('cold_w_inter_termpoint', 'Cold water intermediate terminal point'),('cold_w_dis_termpoint', 'Cold water distant terminal point'),('micro_a', 'Microbiological analysis')])
    pick_up_date=fields.Date('Pick Up Date')
    code=fields.Char('Code')
