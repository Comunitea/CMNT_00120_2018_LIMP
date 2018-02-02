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

from osv import osv, fields
import time
from tools.translate import _

class stock_service_picking_line(osv.osv):

    _name = "stock.service.picking.line"
    _description = "Service picking line"

    def _get_total_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.work_hours + line.tranfer_hours + line.displacement_hours + line.extra_hours

        return res

    _columns = {
        'name': fields.char('Description', size=255, required=True, states={'done':[('readonly',True)]}),
        'vehicle_id': fields.many2one('fleet', 'Vehicle', states={'done':[('readonly',True)]}, ondelete='restrict'),
        'delivery_kms': fields.integer('Delivery kms.', states={'done':[('readonly',True)]}),
        'arrival_kms': fields.integer('Arrival kms.', states={'done':[('readonly',True)]}),
        'delivery_hours': fields.float('Delivery hours', digits=(4,2), states={'done':[('readonly',True)]}),
        'displacement_hours': fields.float('Displacement hours', digits=(4,2), states={'done':[('readonly',True)]}),
        'work_hours': fields.float('Work hours', digits=(4,2), states={'done':[('readonly',True)]}),
        'tranfer_hours': fields.float('Transfer hours', digits=(4,2), states={'done':[('readonly',True)]}),
        'arrival_hours': fields.float('Arrival hours', digits=(4,2), states={'done':[('readonly',True)]}),
        'itinerary': fields.text('Itinerary', states={'done':[('readonly',True)]}),
        'transport_date': fields.datetime('Date', states={'done':[('readonly',True)]}, required=True),
        'transport_date_end': fields.datetime('Date End', states={'done':[('readonly',True)]}),
        'frequency': fields.selection([('sporadic', 'Sporadic'),('monthly','Monthly'),('quarterly', 'Quarterly')], 'Frequency', states={'done':[('readonly',True)]}),
        'transport_type': fields.char('Transport type', size=128, states={'done':[('readonly',True)]}),
        'picking_id': fields.many2one('stock.service.picking', 'Picking', required=True, readonly=True),
        'container_id': fields.related('picking_id', 'container_id', type="many2one", relation="container", string="Container", readonly=True),
        'orig_address_id': fields.many2one('res.partner.address', 'Origin address', states={'done':[('readonly',True)]}),
        'dest_address_id': fields.many2one('res.partner.address', 'Dest. address', states={'done':[('readonly',True)]}),
        'transport_form': fields.selection([('tub', 'Tub'),('container', 'Container'),('other', 'Other')], string="Transport type", states={'done':[('readonly',True)]}),
        'type': fields.selection([('carry', 'Carry'),('remove', 'Remove'),('move', 'Move'),('outstanding','Outstanding'),('other','Other'),
                                  ('aspirating','Aspirating'),('cleaning','Cleaning'),('inplant','Come into plant'),('move_to_plant','Move to plant'),
                                  ('pest_control', 'Pest Control'), ('legionella', 'Legionella')],
                                 'Type', required=True, states={'done':[('readonly',True)]}),
        'other_type_text': fields.char('Type description', size=255, states={'done':[('readonly',True)]}),
        'carrier_id': fields.many2one('res.partner', 'Carrier', states={'done':[('readonly',True)]}),
        'other_carrier': fields.char('Other carrier', size=128, states={'done':[('readonly',True)]}),
        'state': fields.selection([('draft', 'Draft'),('done', 'Done')], 'State', required=True, readonly=True),
        'driver_id': fields.many2one('hr.employee', 'Driver', states={'done':[('readonly',True)]}),
        'waste_type': fields.selection([('clean', 'Clean'),('dirty', 'Dirty')], 'Waste type', states={'done':[('readonly',True)]}),
        'extra_hours': fields.float('Extra Hours',digits=(4,2)),
        'price_hours': fields.float('Price Hours',digits=(4,2)),
        'parent_company_id' : fields.many2one('res.company', 'Parent Company'),
        'parent_man_addr_id': fields.many2one('res.partner.address', 'Manager Address',),
        'parent_building_addr_id': fields.many2one('res.partner.address', 'Building Parent Address'),
        'total_hours': fields.function(_get_total_hours, string='Total hours', type="float", digits=(16,2), method=True, readonly=True),
        'no_print': fields.boolean('No print'),
    }

    _defaults = {
        'delivery_kms': 0.0,
        'arrival_kms': 0.0,
        'delivery_hours': 0.0,
        'displacement_hours': 0.0,
        'work_hours': 0.0,
        'tranfer_hours': 0.0,
        'arrival_hours': 0.0,
        'type': 'carry',
        'frequency': 'sporadic',
        'transport_date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        'state': 'draft',
        'orig_address_id': lambda *a: False,
        'name':lambda self, cr, uid, context: context.get('parent_name',False),
        'dest_address_id': lambda *a: False,
        'parent_company_id' : lambda self, cr, uid, context : context.get('parent_company_id',False) or self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
        'parent_man_addr_id': lambda self, cr, uid, context : context.get('parent_man_addr_id',False),
        'parent_building_addr_id' : lambda self, cr, uid, context : context.get('parent_building_addr_id',False),
    }
    def on_change_type(self,cr,uid,ids,type_,company_id,man_dir_id,building_dir_id):
        res = {'value': {"no_print": False}}
        user_id = self.pool.get('res.users').browse(cr, uid, uid)
        if type_ == 'carry':
            for addr in self.pool.get("res.company").browse(cr,uid,company_id).partner_id.address:
                if addr.containers_store:
                    res['value']['orig_address_id'] = addr.id or user_id.work_address_id.id
                    break
                else:
                    res['value']['orig_address_id'] = user_id.work_address_id.id
            res['value']['dest_address_id'] = building_dir_id
        elif type_ in ('remove', 'inplant', 'move_to_plant'):
            res['value']['orig_address_id'] = building_dir_id or user_id.work_address_id.id
            res['value']['dest_address_id'] = man_dir_id
        else:
            if type_ == "move":
                res["value"]["no_print"] = True
            res['value']['orig_address_id'] = user_id.work_address_id.id
            res['value']['dest_address_id'] = building_dir_id

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res = super(stock_service_picking_line, self).create(cr, uid, vals)
        if vals.get('type',False) in ['remove','inplant','move_to_plant','outstanding','aspirating','cleaning']:
            line = self.browse(cr,uid,res)
            picking = line.picking_id.write({'retired_date':line.transport_date[:10]})
        return res

    def action_done(self, cr, uid, ids, context=None):
        """sets to done and fix current container location"""
        if context is None: context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        obj_hours = self.pool.get("timesheet")
        for line in self.browse(cr, uid, ids):
            if line.container_id and line.dest_address_id:
                line.container_id.write({'situation_id': line.dest_address_id.id,
                                        'container_placement': line.picking_id.container_placement,
                                        'last_move_date': line.transport_date,
                                        'last_responsible_id': line.driver_id and line.driver_id.id or False})
            if line.picking_id.manager_partner_id and line.type in ("remove","inplant") and not line.picking_id.delivery_proof_no:
                if not line.picking_id.manager_partner_id.nima_no:
                    raise osv.except_osv(_('Error !'), _('Manager selected has not NIMA number.'))
                if line.picking_id.manager_partner_id.create_nima_number:
                    seq_id = self.pool.get('ir.sequence').search(cr, uid, [('prefix','=',u"TNP30" + line.picking_id.manager_partner_id.nima_no + time.strftime("%Y")),('code','=',"waste_delivery_proof")])
                    if not seq_id:
                        seq_id = self.pool.get('ir.sequence').create(cr, uid, {
                                                'prefix': u"TNP30" + line.picking_id.manager_partner_id.nima_no + time.strftime("%Y"),
                                                'code': "waste_delivery_proof",
                                                'padding': 7,
                                                'name': u"Waste delivery proof " + line.picking_id.manager_partner_id.name,
                                                'company_id': False
                                            })
                    else:
                        seq_id = seq_id[0]

                    seq = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
                    line.picking_id.write({'delivery_proof_no': seq})

            #~ if line.driver_id and line.picking_id.analytic_acc_id:
                #~ hours = line.work_hours + line.tranfer_hours + line.displacement_hours
                #~ vals = {'hours': hours,
                        #~ 'date': line.transport_date[:10],
                        #~ 'employee_id': line.driver_id.id,
                        #~ 'analytic_id': line.picking_id.analytic_acc_id.id,
                        #~ 'contract': False,
                        #~ 'done': hours and True or False,
                        #~ 'building_site_id':line.picking_id.building_site_id and line.picking_id.building_site_id.id or False,
                        #~ 'department_id': line.picking_id.department_id and line.picking_id.department_id.id or False,
                        #~ 'delegation_id': line.picking_id.delegation_id and line.picking_id.delegation_id.id or False,
                        #~ 'responsible_id': line.picking_id.manager_id and line.picking_id.manager_id.id or False,
                        #~ 'paid': True,
                        #~ 'contract': True,
                        #~ 'done': True
                        #~ }
                #~ obj_hours.create(cr,uid,vals)
                #~ if line.extra_hours:
                    #~ vals = {'extra_hours': line.extra_hours,
                            #~ 'hours': 0.0,
                            #~ 'date': line.transport_date[:10],
                            #~ 'price_hours': line.price_hours,
                            #~ 'employee_id': line.driver_id.id,
                            #~ 'analytic_id': line.picking_id.analytic_acc_id.id,
                            #~ 'pending_qty' : line.price_hours * line.extra_hours,
                            #~ 'contract': False,
                            #~ 'done': False,
                            #~ 'building_site_id': line.picking_id.building_site_id and line.picking_id.building_site_id.id or False,
                            #~ 'department_id': line.picking_id.department_id and line.picking_id.department_id.id or False,
                            #~ 'delegation_id': line.picking_id.delegation_id and line.picking_id.delegation_id.id or False,
                            #~ 'responsible_id': line.picking_id.manager_id and line.picking_id.manager_id.id or False
                            #~ }
                    #~ obj_hours.create(cr,uid,vals)
            #~ elif line.picking_id.picking_type == 'wastes':
                #~ raise osv.except_osv(_('Error, Empty fields !'), _('Driver or analytic_account fields are empty.'))

        return self.write(cr, uid, ids, {'state': 'done'})

    def action_reopen(self, cr, uid, ids, context=None):
        if context is None: context = {}
        for line in self.browse(cr, uid, ids):
            hour_ids = self.pool.get("timesheet").search(cr, uid, [('analytic_id','=',line.picking_id.analytic_acc_id.id),('employee_id','=',line.driver_id.id),('hours', '=', line.work_hours + line.tranfer_hours + line.displacement_hours)])
            hour_ids.extend(self.pool.get("timesheet").search(cr, uid, [('analytic_id','=',line.picking_id.analytic_acc_id.id),('employee_id','=',line.driver_id.id),('extra_hours', '=', line.extra_hours),('hours','=',0.0)]))
            if hour_ids:
                self.pool.get("timesheet").unlink(cr, uid, hour_ids)

            if line.container_id and line.dest_address_id:
                container_move_ids = self.pool.get('container.move').search(cr, uid, [('container_id','=',line.container_id.id)], limit=2)
                if container_move_ids:
                    moves_to_delete = []
                    move = self.pool.get('container.move').browse(cr, uid, container_move_ids[0])
                    if move.address_id.id != line.dest_address_id.id:
                        raise osv.except_osv(_('Error !'), _('You cannot reopen this line because container is not in %s.') % line.dest_address_id.street)
                    moves_to_delete.append(move.id)
                    if move.move_type == 'in':
                        other_move = self.pool.get('container.move').browse(cr, uid, container_move_ids[1])
                        if line.container_id.situation_id and line.container_id.situation_id.id == line.dest_address_id.id:
                            self.pool.get('container').write(cr, uid, [line.container_id.id], {'situation_id': other_move.address_id.id}, context={'no_create_moves': True})
                        moves_to_delete.append(other_move.id)
                    if moves_to_delete:
                        self.pool.get('container.move').unlink(cr, uid, moves_to_delete)

            line.write({'state':'draft'})

            return True

    def unlink(self, cr, uid, ids, context=None):
        if context is None: context = {}
        for obj in self.browse(cr, uid, ids):
            if obj.state != 'draft':
                raise osv.except_osv(_('Error !'), _('Only can delete lines in draft state. Please reopen the line.'))

        return super(stock_service_picking_line, self).unlink(cr, uid, ids, context=context)

stock_service_picking_line()
