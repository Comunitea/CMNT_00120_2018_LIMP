from odoo import models, fields, api


class ServicePickingSignatureWzd(models.TransientModel):
    _name = "service.picking.signature.wzd"
    _description = "Service picking signature wizard"

    picking_id = fields.Many2one('stock.service.picking', 'Service picking', required=True)
    partner_id = fields.Many2one(related='picking_id.partner_id', readonly=True)
    name = fields.Char(string="Name", readonly=True, compute='_compute_name')

    signature_date = fields.Date('Signature date', required=True, default=fields.Date.today())
    signature_name = fields.Char('Signature name', required=True)
    signature_job = fields.Char('Signature job', required=True)
    signature_vat = fields.Char('Signature VAT', required=True)
    signature_image = fields.Binary('Signature', required=True)

    @api.depends('picking_id')
    def _compute_name(self):
        for record in self:
            record.name = "%s - %s" % (record.picking_id.name, record.picking_id.description)

    def action_sign(self):
        self.ensure_one()
        self.picking_id.write({
            'signature_date': self.signature_date,
            'signature_name': self.signature_name,
            'signature_job': self.signature_job,
            'signature_vat': self.signature_vat,
            'signature_image': self.signature_image,
        })
        return {'type': 'ir.actions.act_window_close'}
