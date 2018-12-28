# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LegionellaSamples(models.Model):

    _name = 'legionella.samples'
    _rec_name = "product_id"

    product_id=fields.Many2one("product.product", "Product", required=True)
    registration_number=fields.Char('Registration Number', required=False,
                                    readonly=True,
                                    related="product_id.registration_no")
    type_product=fields.Selection([('acs_acu', 'ACS accumulator'),('acs_inter_terminal', 'ACS intermediate terminal point'),('acs_far_term', 'ACS far terminal'),
    ('cold_w_cistern', 'Cold water cistern'),('cold_w_inter_termpoint', 'Cold water intermediate terminal point'),('cold_w_dis_termpoint', 'Cold water distant terminal point'),('micro_a', 'Microbiological analysis')])
    pick_up_date=fields.Date('Pick Up Date')
    code=fields.Char('Code', readonly=True)
    picking_id=fields.Many2one("stock.service.picking", "Service Picking")
    partner_id = fields.Many2one("res.partner", "Customer",
                                 related="picking_id.partner_id",
                                 readonly=True)
    certificate_no = fields.Char("Certificate no", related="picking_id.n_cert",
                                 readonly=True)
    lab_ship_date=fields.Date("Shipment lab. date")
    lab_recept_date=fields.Date("Reception lab. date")
    observations=fields.Text("Observations")

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].\
            next_by_code('legionella.sample.seq')
        res = super(LegionellaSamples, self).create(vals)
        return res

