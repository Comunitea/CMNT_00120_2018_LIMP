from odoo import models, fields, _


class BuildingSiteServicesLocation(models.Model):
    _name = 'building.site.services.location'
    _description = 'Service picking location'

    name = fields.Char('Location', required=True)
    building_site_services_id = fields.Many2one('building.site.services', 'Service picking')

    _sql_constraints = [
        ('name_uniq', 'unique(name, stock_service_picking_id)', _('The location must be unique per service site'))
    ]


class BuildingSiteServices(models.Model):
    _inherit = 'building.site.services'

    location_ids = fields.One2many(
        'building.site.services.location',
        'building_site_services_id',
        'Locations'
    )
