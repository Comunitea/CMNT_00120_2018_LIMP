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
from odoo.addons import decimal_precision as dp
import time


class StockServicePicking(models.Model):

    _name = "stock.service.picking"
    _description = "Service pickings"
    _inherit = ['mail.thread']
    _inherits = {'account.analytic.account': "analytic_acc_id"}
    _order = "picking_date desc"

    '''def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('service.picking.invoice.concept').browse(cr, uid, ids):
            result[line.service_picking_id.id] = True
        return result.keys()'''

    def _get_all_delegations(self):
        delegation_obj = self.env['res.delegation']
        selection = []
        delegations = self.env['res.delegation'].sudo().search([])
        for delegation in delegations:
            selection.append((str(delegation.id), delegation.name))
        return selection


    state = fields.Selection([('draft', 'Draft'),('active', 'Active'),('closed', 'Closed'),('cancelled', 'Cancelled')], 'State', readonly=True, default='draft')
        #'partner_id = fields.Many2one('res.partner', 'Customer', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
    carrier_id = fields.Many2one('res.partner', 'Carrier', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    manager_partner_id = fields.Many2one('res.partner', 'Manager', help="Destination partner", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    manager_address_id = fields.Many2one('res.partner', 'Address', help="Destination address", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    producer_mark = fields.Selection([('small_producer', 'Small producer'),('producer', 'Producer')], 'Producer type', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    ccc_account_id = fields.Many2one('res.partner.bank', 'Bank', states={'cancelled':[('readonly',True)]}, default=lambda r: r._context.get('ccc_account_id', False), copy=False)
        #'name = fields.Char('Name', size=32, required=True, readonly=True),
    service_ids = fields.One2many('stock.service.picking.line', 'picking_id', 'Transports', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    print_service_ids = fields.One2many('stock.service.picking.line', 'picking_id', 'Transports to print', readonly=True, domain=[('no_print', '=', False)], copy=False)
    move_service_ids = fields.One2many('stock.service.picking.line', 'picking_id', 'Move transports', readonly=True, domain=[('type', '=', 'move')], copy=False)
    remove_service_ids = fields.One2many('stock.service.picking.line', 'picking_id', 'Remove transports', readonly=True, domain=[('type', 'in', ['remove', 'inplant', 'move_to_plant','outstanding','aspirating','cleaning'])], copy=False)
    carry_service_ids = fields.One2many('stock.service.picking.line', 'picking_id', 'Carry transports', readonly=True, domain=[('type', '=', 'carry')], copy=False)
    picking_date = fields.Date('Date', required=True, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    retired_date = fields.Date('Retired Date', copy=False)
    note = fields.Text('Note', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    warning = fields.Text('Warning', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    product_id = fields.Many2one('product.product', 'Product', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    ler_code_id = fields.Many2one('waste.ler.code', 'LER', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    ler_name = fields.Char('Waste', related='ler_code_id.name', readonly=True)
    ler_dangerous = fields.Boolean(related='ler_code_id.dangerous', readonly=True, string="Dangerous")
    gross_weight = fields.Float('Gross (kg.)', digits=(12,2), help="Gross weight in Kg", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    tare = fields.Float('Tare (kg.)', digits=(12,2), help="Tare in Kg.", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    net_weight = fields.Float('Net (kg.)', digits=(12,2), help="Net weight in Kg.", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    volume = fields.Float('Volume (m³)', digits=(12,2), help="Volume in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    container_id = fields.Many2one('container', 'Container', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    container_situation_id = fields.Many2one('res.partner', related='container_id.situation_id',  readonly=True, string="Container situation", copy=False)
    dcs_no = fields.Char('DCS no.', size=24, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    valorization = fields.Boolean('Valorization', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, default=True)
    storage = fields.Boolean('Storage', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    invoice_type = fields.Selection([('toinvoice', 'To invoice'),('invoiced', 'Invoiced'),('noinvoice', 'No invoice')], 'Invoice state',states={'cancelled':[('readonly',True)]}, default='toinvoice', copy=False)
    holder_partner = fields.Char('Holder / Builder',size=255, states={'cancelled':[('readonly',True)]})
    holder_address = fields.Char('Address',size=148, states={'cancelled':[('readonly',True)]})
    producer_partner = fields.Char('Producer', size=255, states={'cancelled':[('readonly',True)]})
    producer_address = fields.Char('Producer Address',size=148, states={'cancelled':[('readonly',True)]})
    building_site_address_id = fields.Many2one('res.partner', 'Building site address', states={'cancelled':[('readonly',True)]})
    building_site_city = fields.Char('City', size=128, states={'cancelled':[('readonly',True)]})
    building_site_license = fields.Char('License', size=64, states={'cancelled':[('readonly',True)]})
    building_site_id = fields.Many2one('building.site.services', 'Building site/Service', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    building_site = fields.Boolean('Building site', help="Demolition and building waste", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    rd_code = fields.Char('R.D. 952/97', size=64, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    overload_qty = fields.Float('Overload', digits=(12,2), help="Overload in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    invoice_date = fields.Date('Invoice date', states={'cancelled':[('readonly',True)]}, copy=False)
    analytic_acc_id = fields.Many2one("account.analytic.account", 'Analytic account', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False, required=True, ondelete="cascade")
        #'company_id = fields.Many2one('res.company', 'Company', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'waste_type = fields.Selection([('clean', 'Clean'),('dirty', 'Dirty')], 'Waste type', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'valorization_company_id = fields.Many2one('res.company', 'Val. company', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'valorization_ler_code_id = fields.Many2one('waste.ler.code', 'Val. LER', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'paint_cans_qty = fields.Float('Paint cans', digits=(12,2), help="Quantity in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #'silicone_cans_qty = fields.Float('Silicone cans', digits=(12,2), help="Quantity in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
        #'isolation_mat_qty = fields.Float('Isolation m.', digits=(12,2), help="Quantity in m³", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    quality = fields.Boolean('Quality', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
        #'other_materials = fields.Char('Other mat.', size=128, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    service_type = fields.Many2one('product.product',string='Service type', states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]})
    stock_picking_id = fields.One2many('stock.picking','stock_service_picking_id',string='Stock picking',states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    fiscal_position = fields.Many2one('account.fiscal.position', 'Fiscal position',states={'cancelled':[('readonly',True)]}, default=lambda r: r._context.get('fiscal_position', False), copy=False)
    payment_term = fields.Many2one('account.payment.term', 'Payment term',states={'cancelled':[('readonly',True)]}, default=lambda r: r._context.get('payment_term', False), copy=False)
    payment_mode = fields.Many2one('account.payment.mode', 'Payment type',states={'cancelled':[('readonly',True)]})
    hours = fields.Float('Hours',states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    service_invoice_concept_ids = fields.One2many('service.picking.invoice.concept', 'service_picking_id', 'Invoice concepts', copy=False)
    other_concepts_ids = fields.One2many('service.picking.other.concepts.rel', 'service_picking_id', 'Other concepts', copy=False)
    nima_no = fields.Char('NIMA', size=255, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, copy=False)
    name_manager = fields.Char('Name manager', size=255, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, default=lambda r: r.env.user.company_id.partner_id.name, copy=False)
    authorization_manager = fields.Char('Authorization Manager', size=32, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, default=lambda r: r.env.user.company_id.partner_id.manager_authorization_no, copy=False)
    picking_type = fields.Selection([('wastes','Wastes'),('sporadic','Sporadic')], 'Type', change_default=True, default=lambda r: r._context.get('type', 'wastes'))
    service_picking_valorization_ids = fields.One2many('service.picking.valorization.rel', 'service_picking_id', 'Valorization', states={'cancelled':[('readonly',True)]}, copy=False)
        #'delegation_id = fields.Many2one('res.delegation', 'Delegation', required=True, states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}),
        #AÑADIDO PARA CALCULAR TOTALES
    taxes = fields.Float('Taxes', digits=(16,2), copy=False)
    product_tax_id = fields.Many2one('product.product', 'Product tax', copy=False)
    sand_amount = fields.Float('Amount', digits=(16,2), copy=False)
    product_sand_id = fields.Many2one('product.product', 'Sand Treatment', copy=False)
    amount_untaxed = fields.Float('Untaxed Amount', digits=dp.get_precision('Sale Price'), compute='_amount_all', help='The amount without tax.')
    amount_tax = fields.Float('Taxes', digits=dp.get_precision('Sale Price'), compute='_amount_all', help='The tax amount.')
    amount_total = fields.Float('Total with taxes', digits=dp.get_precision('Sale Price'), compute='_amount_all', help='The total amount.')
    picking_date = fields.Date('Picking date', required=True, default=fields.Date.today(), copy=False)
    service_id = fields.Many2one('waste.service', 'Waste service', readonly=True)
    intercompany = fields.Boolean('Intercompay')
        #'invoice_delegation_id = fields.Many2one('res.delegation', 'Delegation', help="Delegation where inputs the cost"),
    invoice_delegation_id = fields.Selection(_get_all_delegations, string="Delegation", help="Delegation where inputs the cost")
    invoice_department_id = fields.Many2one('hr.department', 'Department', help="Department where inputs the cost")
    invoice_responsible_id = fields.Many2one('hr.employee', 'Responsible', help="Responsible who inputs the cost", domain=[('responsible', '=', True)])
    delivery_proof_no = fields.Char('Delivery proof no.', size=128, readonly=True, copy=False)
    not_print_acceptation = fields.Boolean('Not print acceptation', help="Not print acceptation in delivery waste check report")
    older = fields.Boolean('Older')
    internal_notes = fields.Text('Notes')
    planified = fields.Boolean('Planified')
    container_placement = fields.Selection([('on_street', 'On street'),('on_building', 'On building')], string="Container placement", states={'closed':[('readonly',True)],'cancelled':[('readonly',True)]}, default='on_building')
    maintenance = fields.Boolean('Maintenance')
    #name = fields.Char(default='SEQ')
    sale_id = fields.Many2one("sale.order", string="Sale")

    def _amount_all(self):
        for picking in self:
            am_tax = am_untax = 0.0
            for inv_cncpt in picking.service_invoice_concept_ids:
                am_untax += inv_cncpt.subtotal
                am_tax += inv_cncpt._amount_line_tax()
            if picking.product_sand_id and picking.sand_amount:
                for c in picking.product_sand_id.taxes_id.compute_all(picking.sand_amount, 1, picking.product_sand_id)['taxes']:
                    am_tax += c.get('amount', 0.0)
                am_untax += picking.sand_amount

            picking.amount_tax = am_tax
            picking.amount_untaxed = am_untax
            picking.amount_total = am_untax + am_tax + (picking.taxes or 0.0)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        part = self.partner_id
        if self._context.get('service_id', False):
            service = self.env['waste.service'].browse(self._context.get('service_id', False))

            self.address_invoice_id = service.address_invoice_id and service.address_invoice_id.id or service.contact_id.id
            self.address_id = service.partner_shipping_id and service.partner_shipping_id.id or service.contact_id.id
            self.ccc_account_id = (service.payment_mode and service.payment_mode.suitable_bank_types and service.partner_bank_id) and part.partner_bank_id.id or False
            self.fiscal_position =service.fiscal_position and service.fiscal_position.id or False
            self.payment_term = service.payment_term and service.payment_term.id or False
            self.payment_mode = service.payment_mode and service.payment_mode.id or False
            self.intercompany = False
            part = service.partner_id

        else:
            if not part:
                self.address_id = False
                self.address_invoice_id = False
                self.orig_address_id = False
                return

            addr = part.address_get(['contact', 'invoice', 'default'])
            payment = part.customer_payment_mode_id and part.customer_payment_mode_id or False

            self.address_invoice_id = addr['invoice']
            self.address_id = addr['contact']
            self.ccc_account_id = (payment and payment.suitable_bank_types and part.bank_ids) and part.bank_ids[0].id or False
            self.fiscal_position =part.property_account_position_id and part.property_account_position_id.id or False
            self.payment_term = part.property_payment_term_id and part.property_payment_term_id.id or False
            self.payment_mode = payment and payment.id or False
            self.intercompany = False

        if self.env.user.company_id.partner_id.id == part.id:
            self.intercompany = True

        if part.picking_warn_type != 'no-message':
            warning = {}
            title = _("Warning for %s") % part.name
            message = part.picking_warn_message
            warning['title'] = title
            warning['message'] = message
            if part.picking_warn_type == 'block':
                self.partner_id = False
            return {'warning':warning}

    @api.onchange('manager_partner_id')
    def onchange_manager_partner_id(self):
        if not self.partner_id:
            self.manager_address_id = False
            return
        nima = False
        addr = self.partner_id.address_get(['management_plant'])
        if self.partner_id.nima_no:
            nima = self.partner_id.nima_no

        self.manager_address_id = addr['management_plant']
        self.nima_no = nima
        self.name_manager = self.partner_id.name
        self.authorization_manager = self.partner_id.manager_authorization_no and self.partner_id.manager_authorization_no or False

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        if self.product_id.ler_code_id:
            self.ler_code_id = self.product_id.ler_code_id.id
        else:
            self.ler_code_id = False

        if self.product_id.picking_warn != 'no-message':
            warning = {}
            title = _("Warning for %s") % self.product_id.name
            message = self.product_id.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
            if self.product_id.picking_warn == 'block':
                self.product_id = False
            return {'warning': warning}

    @api.onchange('building_site_id')
    def onchange_building_site_id(self):
        if self.building_site_id:
            if self.building_site_id:
                self.building_site_address_id = self.building_site_id.address_building_site.id
                self.building_site_city = self.building_site_id.city_building_site
                self.building_site_license = self.building_site_id.building_site_license
                self.holder_partner = self.building_site_id.holder_builder
                self.holder_address = self.building_site_id.address_holder
                self.producer_partner = self.building_site_id.producer_promoter
                self.producer_address = self.building_site_id.address_producer

        else:
            self.building_site_address_id = False
            self.building_site_city = False
            self.building_site_license = False
            self.holder_partner = False
            self.holder_address = False
            self.producer_partner = False
            self.producer_address = False

    @api.onchange('service_type')
    def onchange_service_type(self):
        if not self.service_type:
            return
        if self.service_type.picking_warn != 'no-message':
            warning = {}
            title = _("Warning for %s") % self.service_type.name
            message = self.service_type.picking_warn_msg
            warning['title'] = title
            warning['message'] = message
            if self.service_type.picking_warn == 'block':
                self.service_type = False
        return {'warning':warning}

    @api.model
    def create(self, vals):
        """Add a sequence name"""
        if not vals.get('maintenance'):
            seq = self.env['ir.sequence'].next_by_code('stock.service.picking')
        else:
            seq = self.env['ir.sequence'].next_by_code('service.picking.maintenance')
        vals['name'] = seq
        vals['state'] = 'draft'
        res = super(StockServicePicking, self).create(vals)
        return res

    def action_active(self):
        return self.write({'state': 'active'})

    def create_concept_lines(self):
        for order in self:
            if order.service_invoice_concept_ids:
                order.service_invoice_concept_ids.unlink()

            seq = 1
            for waste in order.service_picking_valorization_ids:
                if waste.billable:
                    if waste.product_qty and waste.product_id:
                        vals = {
                        'sequence': seq,
                        'product_id': waste.product_id.id,
                        'name': waste.name,
                        'product_qty': waste.product_qty,
                        'product_uom': waste.product_id.uom_id.id,
                        'price': waste.product_id.list_price,
                        'service_picking_id': order.id,
                        'tax_ids': [(6,0,[x.id for x in waste.product_id.taxes_id])],
                        'price': waste.product_id.list_price
                        }
                        self.env['service.picking.invoice.concept'].create(vals)
                        seq += 1

                if waste.overload_qty and (waste.product_id and waste.product_id.overload_price):
                    vals = {
                        'product_id': waste.product_id.id,
                        'sequence': seq,
                        'name': _('Overload/') + waste.product_id.name_get()[0][1],
                        'product_qty': waste.overload_qty,
                        'product_uom': waste.product_id.uom_id.id,
                        'price': waste.product_id.overload_price,
                        'service_picking_id': order.id,
                        'tax_ids': [(6,0,[x.id for x in waste.product_id.taxes_id])]
                    }

                    self.env['service.picking.invoice.concept'].create(cr, uid, vals)
                    seq += 1

            for other_concept in order.other_concepts_ids:
                if other_concept.billable:
                    vals = {
                        'sequence': seq,
                        'product_id': other_concept.product_id.id,
                        'name': other_concept.name,
                        'product_qty': other_concept.product_qty,
                        'product_uom': other_concept.product_id.uom_id.id,
                        'price': other_concept.price_unit,
                        'service_picking_id': order.id,
                        'tax_ids': [(6,0,[x.id for x in other_concept.product_id.taxes_id])]
                    }

                    self.env['service.picking.invoice.concept'].create(vals)
                    seq += 1
        return True

    def action_close(self):
        for order in self:
            if order.service_ids.filtered(lambda r: r.state != 'done'):
                raise UserError(_('Cannot close because you have transports in draft state.'))

            picking_id = False
            location_id = False
            location_dest_id = False

            if order.intercompany and not order.no_quality:
                raise UserError(_('Cannot close because you have checked intercompany and you have not checked scont.'))

            if order.picking_type == "wastes" and not order.retired_date:
                retired_date = False
                for line in order.remove_service_ids:
                    if not retired_date or retired_date < line.transport_date[:10]:
                        retired_date = line.transport_date

                if retired_date:
                    order.write({'retired_date':retired_date})
                else:
                    raise UserError(_('You are trying to close a service picking without retired date.'))
            elif order.picking_type == "wastes" and order.retired_date:
                for line in order.remove_service_ids:
                    if order.retired_date < line.transport_date[:10]:
                        raise UserError(_('You are trying to close a service picking with wrong retired date.'))
                if order.retired_date < order.picking_date:
                    raise UserError(_('You are trying to close a service picking with wrong retired date.'))
            elif order.picking_type == "sporadic":
                order.write({'retired_date': order.picking_date})

            company = self.env['res.company'].sudo().search([('partner_id', '=', order.manager_partner_id.id)])
            if company:
                current_company = self.env.user.company_id
                if current_company.id == company.id:
                    addr = order.address_id.id
                else:
                    addr = current_company.partner_id.id

                location_id = self.env.ref('stock.stock_location_customers').id
                warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id', '=', company.id)])
                if not warehouse_ids:
                    raise osv.except_osv(_('Error !'), _('There is no wharehouse to the order company'))
                location_dest_id = warehouse_ids[0].lot_stock_id.id

                for valorization_line in order.service_picking_valorization_ids:
                    if valorization_line.overload_qty and (valorization_line.product_id and not valorization_line.product_id.overload_price):
                        raise UserError(_('You are trying to close a service picking with overload quantity but the product has not the overload price. Please fill it!'))

                    if not picking_id:
                        pick_type = self.env['stock.picking.type'].sudo().\
                            search([('warehouse_id', '=', warehouse_ids[0].id),
                                    ('code','=', 'incoming')])
                        pick_name = pick_type.sequence_id.next_by_id()
                        picking_id = self.env['stock.picking'].sudo().create({
                            'name': u'S' + pick_name,
                            'origin': order.name,
                            'picking_type_id': pick_type.id,
                            'state': 'draft',
                            'address_id': addr,
                            'no_quality': order.no_quality,
                            'company_id': company.id,
                            'stock_service_picking_id': order.id,
                            'from_spicking' : True,
                            'date': order.retired_date or order.picking_date,
                            'location_id': location_id,
                            'location_dest_id':location_dest_id,
                            'invoice_type': 'out_invoice',
                            'invoice_state' : current_company.id == company.id and 'none' or'2binvoiced'
                        })

                    if (valorization_line.product_id.company_id.id == company.parent_id.id) or (not valorization_line.product_id.company_id) or (valorization_line.product_id.company_id.id == company.id):
                        move_id = self.env['stock.move'].sudo().create({
                                'name': order.name,
                                'picking_id': picking_id.id,
                                'product_id': valorization_line.product_id.id,
                                'product_uom_qty': valorization_line.product_qty + valorization_line.overload_qty,
                                'product_uom': valorization_line.product_id.uom_id.id,
                                'address_id': addr,
                                'location_id': location_id,
                                'location_dest_id':location_dest_id,
                                'tracking_id': False,
                                'date': order.retired_date or order.picking_date,
                                'date_expected': order.retired_date or order.picking_date,
                                'state': 'draft',
                                'company_id': company.id,
                            })
                    else:
                        raise UserError(_('Product %s must be shared inter companies for proceeding') % valorization_line.product_id.name)

                if picking_id:
                    self.env['stock.immediate.transfer'].sudo().create({'pick_id': picking_id.id}).process()
            order.analytic_acc_id.write({'state': 'close', 'date': order.retired_date or order.picking_date})

        self.create_concept_lines()
        return self.write({'state': 'closed'})

    def action_cancel(self):
        return self.write({'state': 'cancelled'})

    def action_draft(self):
        return self.write({'state':'draft'})
