# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MonthsInterval(models.Model):

    _name = 'months.interval'

    name=fields.Char(required=True)
    code=fields.Char(required=True)
