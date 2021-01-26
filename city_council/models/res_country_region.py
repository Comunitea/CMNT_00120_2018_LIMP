# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResCountryRegion(models.Model):

    _name = "res.country.region"
    _description = 'Region'
    _order = 'name'

    country_id = fields.Many2one('res.country', 'Country', required=True)
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=10)


class ResCountryState(models.Model):

    _inherit = 'res.country.state'

    region_id = fields.Many2one('res.country.region', 'Region')
