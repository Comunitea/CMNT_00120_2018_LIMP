from odoo import models, fields, api, _
import locale


class LimpCertResGoa(models.Model):
    _name = 'limp.cert.res.goa'
    _description = 'Certificado de gestión de residuos GOA'

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        default=lambda self: _('New'), compute='_compute_name',
        store=True
    )
    date = fields.Date('Date', default=fields.Date.context_today)
    date_init = fields.Date('Date init', required=True)
    date_end = fields.Date('Date end', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, domain=[('is_company', '=', True)])
    building_site_id = fields.Many2one('building.site.services', 'Building site', required=True)
    line_ids = fields.One2many(
        'limp.cert.res.goa.line',
        'cert_res_goa_id',
        'Lines',
        readonly=False,
        compute='_compute_service_pickings',
        store=True,
        ondelete='cascade'
    )

    def _translate_date(self):
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        return self.date.strftime('%d de %B de %Y')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.building_site_id = False

    @api.depends('date', 'partner_id.name', 'building_site_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.date and rec.partner_id and rec.building_site_id:
                rec.name = str(rec.date) + ' - ' + rec.partner_id.name + ' - ' + rec.building_site_id.name

    @api.depends('date_init', 'date_end', 'partner_id', 'building_site_id')
    def _compute_service_pickings(self):
        for cert in self:
            if cert.date_init and cert.date_end and cert.partner_id and cert.building_site_id:
                service_picking_ids = self.env['stock.service.picking'].search([
                    ('retired_date', '>=', cert.date_init),
                    ('retired_date', '<=', cert.date_end),
                    ('partner_id', '=', cert.partner_id.id),
                    ('building_site_id', '=', cert.building_site_id.id),
                    ('state', '=', 'closed'),
                ]).filtered('service_picking_valorization_ids')
                cert.line_ids = [(5,)]
                if service_picking_ids:
                    cert.line_ids = [(0, 0, {
                        'date': service_picking.retired_date,
                        'producer_id': service_picking.producer_promoter_id.id,
                        'ler': service_picking.service_picking_valorization_ids[0].ler_code,
                        'description': service_picking.service_picking_valorization_ids[0].name,
                        'weight': service_picking.service_picking_valorization_ids[0].net_weight,
                        'dcs_no': service_picking.dcs_no,
                        'percentage':
                            service_picking.service_picking_valorization_ids[0].product_id.valorization_percentage,
                    }) for service_picking in service_picking_ids]
            else:
                cert.line_ids = [(5,)]


class LimpCertResGoaLine(models.Model):
    _name = 'limp.cert.res.goa.line'
    _description = 'Línea de certificado de residencia en Goa'
    _order = 'date asc'

    cert_res_goa_id = fields.Many2one('limp.cert.res.goa', 'Certificado de residencia en Goa')

    date = fields.Date('Date')
    producer_id = fields.Many2one('res.partner', 'Producer')
    nif = fields.Char('NIF', related='producer_id.vat')
    dcs_no = fields.Char('DCS Nº', size=26)
    ler = fields.Char('LER', size=20)
    description = fields.Char('Description')
    weight = fields.Float('Weight')
    percentage = fields.Float('Percentage')
