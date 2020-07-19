from odoo import models, fields, api


class MonthsInterval(models.Model):

    _name = "months.interval"
    _order = "code asc"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
