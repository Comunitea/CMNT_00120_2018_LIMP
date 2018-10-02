# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockServicePickingDDD(models.Model):
    _inherit = 'stock.service.picking'

    n_cert=fields.Char('Nº certificate Legionella', readonly=True)
    n_cert_ddd=fields.Char('Nº certificate DDD', readonly=True)
    type_ddd_ids=fields.Many2many('types.ddd', string='Types ddd')
    treatment_applicator1=fields.Many2one('hr.employee', string='Treatment Applicator 1')
    treatment_applicator2=fields.Many2one('hr.employee', string='Treatment Applicator 2')
    technical_support=fields.Many2one('hr.employee', string="Technical Support")

    start_time=fields.Float(digits=(4,2), string="Start time")
    end_time=fields.Float(digits=(4,2), string="End time")

    start_time_str=fields.Char(compute='_str_date')
    end_time_str=fields.Char(compute='_str_date')
    signer_name = fields.Char("Signer Name")
    signer_id = fields.Char("Signer VAT")

    #Page DDD

    detected_species_id=fields.One2many('detected.species',  'picking_id', string="Detected Species")

    products_used_id=fields.One2many('products.used', 'picking_id', string ="Products Used")

    monitoring_situation=fields.Char('Monitoring situation')

    observations_recommendations=fields.Many2many('observation.recommendation.ddd', string ="Observations/Recommendations")

    dr=fields.Boolean(compute ="_get_dr")
    df=fields.Boolean(compute ="_get_dr")
    ds=fields.Boolean(compute ="_get_dr")
    lg=fields.Boolean(compute ="_get_dr")


    ##Page Legionella

    type_of_installation_id=fields.Many2one('type.of.installation.legionella', string="Type of installation legionella")
    date_of_notification=fields.Date(string ="Date of notification", help="Date of notification to the competent autority")
    legionella_products_id=fields.One2many('legionella.samples', 'picking_id', string="Legionella samples")
    used_product_ids = fields.Many2many('product.product', string="Products used")

    @api.multi
    def _str_date(self):
        for x in self:

            if x.start_time:

                time = x.start_time

                hours = int(time)
                minutes = (time*60) % 60
                seconds = (time*3600) % 60

                x.start_time_str="%d:%02d:%02d" % (hours, minutes, seconds)


            if x.end_time:
                time = x.end_time

                hours = int(time)
                minutes = (time*60) % 60
                seconds = (time*3600) % 60

                x.end_time_str="%d:%02d:%02d" % (hours, minutes, seconds)



    @api.depends('type_ddd_ids')
    def _get_dr(self):

        for pickin in self:
            type_ddd_str=u','.join([x.code for x in pickin.type_ddd_ids])

            if "desratizacion" in type_ddd_str:
                pickin.dr=True

            if "desinfeccion" in type_ddd_str:
                pickin.df=True

            if "desinsectacion" in type_ddd_str:
                pickin.ds=True

            if "legionella" in type_ddd_str:
                pickin.lg=True

    @api.model
    def create(self, vals):
        picking = super(StockServicePickingDDD, self).create(vals)
        if vals.get('type_ddd_ids'):
            create_ddd_seq = False
            for service in picking.type_ddd_ids:
                if not create_ddd_seq and service.service_type == 'ddd':
                    create_ddd_seq = True
                    picking.n_cert_ddd = \
                        self.env['ir.sequence'].\
                        next_by_code('treatment.certificate.ddd')
                elif service.service_type == 'legionella':
                    picking.n_cert = \
                        self.env['ir.sequence'].\
                        next_by_code('treatment.certificate.legionella')

        return picking

    @api.multi
    def write(self, vals):
        res = super(StockServicePickingDDD, self).write(vals)
        if vals.get('type_ddd_ids'):
            for picking in self:
                for service in picking.type_ddd_ids:
                    if service.service_type == 'ddd' and \
                            not picking.n_cert_ddd:
                        picking.n_cert_ddd = \
                            self.env['ir.sequence'].\
                            next_by_code('treatment.certificate.ddd')
                    elif service.service_type == 'legionella' \
                            and not picking.n_cert:
                        picking.n_cert = \
                            self.env['ir.sequence'].\
                            next_by_code('treatment.certificate.legionella')

        return res



