# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time


class StockServicePickingLine(models.Model):

    _name = "stock.service.picking.line"
    _description = "Service picking line"

    name = fields.Char('Description', size=255, required=True, states={'done':[('readonly',True)]}, default=lambda r: r._context.get('parent_name', False))
    vehicle_id = fields.Many2one('fleet', 'Vehicle', states={'done':[('readonly',True)]}, ondelete='restrict')
    delivery_kms = fields.Integer('Delivery kms.', states={'done':[('readonly',True)]})
    arrival_kms = fields.Integer('Arrival kms.', states={'done':[('readonly',True)]})
    delivery_hours = fields.Float('Delivery hours', digits=(4,2), states={'done':[('readonly',True)]})
    displacement_hours = fields.Float('Displacement hours', digits=(4,2), states={'done':[('readonly',True)]})
    work_hours = fields.Float('Work hours', digits=(4,2), states={'done':[('readonly',True)]})
    tranfer_hours = fields.Float('Transfer hours', digits=(4,2), states={'done':[('readonly',True)]})
    arrival_hours = fields.Float('Arrival hours', digits=(4,2), states={'done':[('readonly',True)]})
    itinerary = fields.Text('Itinerary', states={'done':[('readonly',True)]})
    transport_date = fields.Datetime('Date', states={'done':[('readonly',True)]}, required=True, default=fields.Datetime.now())
    transport_date_end = fields.Datetime('Date End', states={'done':[('readonly',True)]})
    frequency = fields.Selection([('sporadic', 'Sporadic'),('monthly','Monthly'),('quarterly', 'Quarterly')], 'Frequency', states={'done':[('readonly',True)]}, default='sporadic')
    transport_type = fields.Char('Transport type', size=128, states={'done':[('readonly',True)]})
    picking_id = fields.Many2one('stock.service.picking', 'Picking', required=True, readonly=True)
    container_id = fields.Many2one('container', 'Container', related='picking_id.container_id', readonly=True)
    orig_address_id = fields.Many2one('res.partner', 'Origin address', states={'done':[('readonly',True)]})
    dest_address_id = fields.Many2one('res.partner', 'Dest. address', states={'done':[('readonly',True)]})
    transport_form = fields.Selection([('tub', 'Tub'),('container', 'Container'),('other', 'Other')], string="Transport type", states={'done':[('readonly',True)]})
    type = fields.Selection([('carry', 'Carry'),('remove', 'Remove'),('move', 'Move'),('outstanding','Outstanding'),('other','Other'),
                              ('aspirating','Aspirating'),('cleaning','Cleaning'),('inplant','Come into plant'),('move_to_plant','Move to plant'),
                              ('pest_control', 'Pest Control'), ('legionella', 'Legionella')],
                             'Type', required=True, states={'done':[('readonly',True)]}, default='carry')
    other_type_text = fields.Char('Type description', size=255, states={'done':[('readonly',True)]})
    carrier_id = fields.Many2one('res.partner', 'Carrier', states={'done':[('readonly',True)]})
    other_carrier = fields.Char('Other carrier', size=128, states={'done':[('readonly',True)]})
    state = fields.Selection([('draft', 'Draft'),('done', 'Done')], 'State', required=True, readonly=True, default='draft')
    driver_id = fields.Many2one('hr.employee', 'Driver', states={'done':[('readonly',True)]})
    waste_type = fields.Selection([('clean', 'Clean'),('dirty', 'Dirty')], 'Waste type', states={'done':[('readonly',True)]})
    extra_hours = fields.Float('Extra Hours',digits=(4,2))
    price_hours = fields.Float('Price Hours',digits=(4,2))
    parent_company_id = fields.Many2one('res.company', 'Parent Company', default=lambda r: r._context.get('parent_company_id', r.env.user.company_id.id))
    parent_man_addr_id = fields.Many2one('res.partner', 'Manager Address', default=lambda r: r._context.get('parent_man_addr_id', False))
    parent_building_addr_id = fields.Many2one('res.partner', 'Building Parent Address', default=lambda r: r._context.get('parent_building_addr_id', False))
    total_hours = fields.Float('Total hours', digits=(16, 2), compute='_compute_total_hours')
    no_print = fields.Boolean('No print')

    def _compute_total_hours(self):
        for line in self:
            line.total_hours = line.work_hours + line.tranfer_hours + line.displacement_hours + line.extra_hours

    @api.onchange('type')
    def on_change_type(self):
        no_print = False
        if self.type == 'carry':
            for addr in self.parent_company_id.partner_id.child_ids.filtered(lambda r: r.type != 'contact'):
                if addr.containers_store:
                    self.orig_address_id = addr.id
                    break
                else:
                    self.orig_address_id = self.env.user.work_address_id.id
            self.dest_address_id = self.parent_building_addr_id
        elif self.type in ('remove', 'inplant', 'move_to_plant'):
            self.orig_address_id = self.parent_building_addr_id or self.env.user.work_address_id.id
            self.dest_address_id = self.parent_man_addr_id
        else:
            if self.type == "move":
                no_print = True
            self.orig_address_id = self.env.user.work_address_id.id
            self.dest_address_id = self.parent_building_addr_id
        self.no_print = no_print

    @api.model
    def create(self, vals):
        res = super(StockServicePickingLine, self).create(vals)
        if vals.get('type',False) in ['remove','inplant','move_to_plant','outstanding','aspirating','cleaning']:
            picking = res.picking_id.write({'retired_date':res.transport_date[:10]})
        return res

    @api.multi
    def action_done(self):
        for line in self:
            if line.container_id and line.dest_address_id:
                line.container_id.write({'situation_id': line.dest_address_id.id,
                                        'container_placement': line.picking_id.container_placement,
                                        'last_move_date': line.transport_date,
                                        'last_responsible_id': line.driver_id and line.driver_id.id or False})
            if line.picking_id.manager_partner_id and line.type in ("remove","inplant") and not line.picking_id.delivery_proof_no:
                if not line.picking_id.manager_partner_id.nima_no:
                    raise UserError(_('Manager selected has not NIMA number.'))
                if line.picking_id.manager_partner_id.create_nima_number:
                    seq_id = self.env['ir.sequence'].search([('prefix','=',u"TNP30" + line.picking_id.manager_partner_id.nima_no + time.strftime("%Y")),('code','=',"waste_delivery_proof")])
                    if not seq_id:
                        seq_id = self.env['ir.sequence'].create(
                        {
                            'prefix': u"TNP30" + line.picking_id.manager_partner_id.nima_no + time.strftime("%Y"),
                            'code': "waste_delivery_proof",
                            'padding': 7,
                            'name': u"Waste delivery proof " + line.picking_id.manager_partner_id.name,
                            'company_id': False
                        })
                    else:
                        seq_id = seq_id[0]

                    seq = seq_id.next_by_id()
                    line.picking_id.write({'delivery_proof_no': seq})
        return self.write({'state': 'done'})

    @api.multi
    def action_reopen(self):
        for line in self:
            if line.container_id and line.dest_address_id:
                container_move_ids = self.env['container.move'].search([('container_id','=',line.container_id.id)], limit=2)
                if container_move_ids:
                    moves_to_delete = self.env['container.move']
                    move = container_move_ids[0]
                    if move.address_id.id != line.dest_address_id.id:
                        raise UserError(_('You cannot reopen this line because container is not in %s.') % line.dest_address_id.street)
                    moves_to_delete += move
                    if move.move_type == 'in':
                        other_move = container_move_ids[1]
                        if line.container_id.situation_id and line.container_id.situation_id.id == line.dest_address_id.id:
                            line.container_id.with_context(no_create_moves=True).write({'situation_id': other_move.address_id.id})
                        moves_to_delete += other_move
                    if moves_to_delete:
                        moves_to_delete.unlink()
            line.write({'state':'draft'})

            return True

    @api.multi
    def unlink(self):
        if self.filtered(lambda r: r.state != 'draft'):
            raise UserError(_('Only can delete lines in draft state. Please reopen the line.'))

        return super(StockServicePickingLine, self).unlink()
