# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
from datetime import datetime,timedelta


class SaleOrder(models.Model):

    _inherit = 'sale.order'
    _order = "date_order desc"

    '''def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'margin':0.0,
                'margin_percentage': 0.0
            }
            val = 0.0
            val1 = 0.0
            valmargin = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                valmargin += line.margin or 0.0
            if order.periodicity_id:
                val1 = val1 * order.periodicity_id.multiplier
                val = val * order.periodicity_id.multiplier
                if order.periodicity_id.rounding:
                    val1 = round(val1,0)
                    val = round(val,0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            res[order.id]['margin'] = cur_obj.round(cr, uid, cur, valmargin)
            res[order.id]['margin_percentage'] = cur_obj.round(cr, uid, cur, ((res[order.id]['margin'] * 100.0) / (res[order.id]['amount_untaxed'] or 1.0)))
        return res'''

    #'freq_table = fields.Text('Frequency table'),
    periodicity_id = fields.Many2one('sale.order.periodicity', 'Periodicity', help="Multiply total amount by periodicity value")
    delegation_id = fields.Many2one('res.delegation', 'Delegation', required=True, change_default=True, default=lambda r: r.env.user.context_delegation_id.id)
    department_id = fields.Many2one('hr.department', 'Department', required=True, change_default=True, default=lambda r: r.env.user.context_department_id.id)
    center_type_id = fields.Many2one("limp.center.type", "Center type", change_default=True)
    contract_ids = fields.One2many('limp.contract', 'sale_id', string="Contracts", readonly=True, copy=False)
    created_contract = fields.Boolean('Created contract', readonly=True, copy=False)
    created_service_order = fields.Boolean('Created Service order', readonly=True, copy=False)
    created_service_pick = fields.Boolean('Created Service pick', readonly=True, copy=False)
    service_order_ids = fields.One2many('waste.service', 'sale_id', string='Service orders', readonly=True, copy=False)
    task_frequency_ids = fields.One2many('task.frequency', 'sale_id', 'Task Frequency')
    validity_Date = fields.Date('End of validity')
    very_important_text = fields.Text('Very important')
    header_notes = fields.Text('Header notes')
    show_total = fields.Boolean("Show total in report", default=True)
    name = fields.Char(default='/')

    @api.model
    def create(self, vals):
        if vals.get('name', False) == "/":
            vals["name"] = self.env['ir.sequence'].next_by_code('sale.order')
        if not vals.get('validity_date', False):
            formatted_date = datetime.strptime(vals['date_order'], "%Y-%m-%d %H:%M:%S")
            vals['validity_date'] = datetime.strftime(formatted_date + timedelta(days=30),"%Y-%m-%d")
        return super(SaleOrder, self).create(vals)

    def get_all_tasks(self):
        """Load all task related with this sale order"""
        for order in self:
            if not order.department_id:
                raise UserError(_('Not department defined for this sale order'))
            task_ids = self.env['limp.contract.task'].search(
                ['|', ('department_id', '=', order.department_id.id),
                 ('department_id', '=', False), '|',
                 ('center_type_id', '=', order.center_type_id.id),
                 ('center_type_id', '=', False)])
            for task in task_ids:
                self.env['task.frequency'].create(
                    {'task_id': task.id, 'sale_id': order.id,
                     'sequence': task.sequence})
        return True

    '''def action_ship_create(self, cr, uid, ids, *args):
        res = super(SaleOrder, self).action_ship_create(cr, uid, ids, args)

        for order in self.browse(cr, uid, ids):
            if order.order_policy != 'picking':
                picking_ids = self.pool.get('stock.picking').search(cr, uid, [('sale_id', '=', order.id)])
                if picking_ids:
                    move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', picking_ids)])
                    self.pool.get('stock.picking').write(cr, uid, picking_ids, {'state': 'draft'})
                    self.pool.get('stock.move').write(cr, uid, move_ids, {'state': 'draft', 'picking_id': False})
                    self.pool.get('stock.move').unlink(cr, uid, move_ids)
                    self.pool.get('stock.picking').unlink(cr, uid, picking_ids)

        return res'''

    def create_contract(self):

        contract_id = self.env['limp.contract'].create({
            'company_id': self.company_id.id,
            'delegation_id': self.delegation_id.id,
            'department_id': self.department_id.id,
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'address_id': self.partner_shipping_id.id,
            'bank_account_id': self.partner_bank and self.partner_bank.id or False,
            'payment_term_id': self.payment_term and self.payment_term.id or False,
            'payment_type_id': self.payment_mode_id and self.payment_mode_id.id or False,
            'address_invoice_id': self.partner_invoice_id.id,
            'sale_id': self.id
        })

        self.write({'created_contract': True})

        res = self.env.ref('limp_contract.limp_contract_form')

        return {
            'name': 'Contract',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res.id],
            'res_model': 'limp.contract',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': contract_id,
        }

    def create_service_order(self):
        vals = {
            'partner_id': self.partner_id.id,
            'contact_id': self.partner_order_id.id,
            'address_invoice_id': self.partner_invoice_id.id,
            'company_id': self.company_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'sale_id': self.id,
            'payment_term': self.payment_term and self.payment_term.id or False,
            'payment_type': self.payment_type and self.payment_type.id or False,
            'partner_bank_id': self.partner_bank and self.partner_bank.id or False,
            'fiscal_position': self.fiscal_position and self.fiscal_position.id or False
        }
        service_order_id = self.env['waste.service'].create(vals)
        self.write({'created_service_order': True})

        res = self.env.ref('limp_service_picking.waste_service_form')

        return {
            'name': 'Service order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res.id],
            'res_model': 'waste.service',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': service_order_id
        }

    def create_pick(self):
        vals = {
            'partner_id': self.partner_id.id,
            'address_id': self.partner_order_id.id,
            'contact_id': self.partner_order_id.id,
            'address_invoice_id': self.partner_invoice_id.id,
            'company_id': self.company_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'sale_id': self.id,
            'picking_type': self._context['picking_type'],
            'payment_term': self.payment_term and self.payment_term.id or False,
            'payment_type': self.payment_type and self.payment_type.id or False,
            'partner_bank_id': self.partner_bank and self.partner_bank.id or False,
            'fiscal_position': self.fiscal_position and self.fiscal_position.id or False,
            'delegation_id': self.delegation_id.id,
            'department_id': self.department_id.id
        }
        if self._context['picking_type'] == "maintenance":
            vals["maintenance"] = True
            vals["picking_type"] = "sporadic"
        service_pick_id = self.env['stock.service.picking'].create(vals)
        self.write({'created_service_pick': True})

        if self._context['picking_type'] == 'wastes':
            res = self.env.ref('limp_service_picking.stock_service_picking_form')
        else:
            res = self.env.ref('limp_service_picking.stock_sporadic_service_picking_form')

        return {
            'name': 'Service picking',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res.id],
            'res_model': 'stock.service.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': service_pick_id
        }


'''class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
                if line.purchase_price:
                    res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.purchase_price*line.product_uos_qty), 2)
                else:
                    res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.product_id.standard_price*line.product_uos_qty), 2)
        return res

    def _get_tax_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = self.pool.get('sale.order')._amount_line_tax(cr, uid, line, context=context)

        return res

    _columns = {
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'margin': fields.function(_product_margin, string='Margin',
              store = True, method=True),
        'purchase_price': fields.float('Cost Price', digits=(16,2)),
        'tax_amount': fields.function(_get_tax_amount, method=True,
                                      string="Tax amount", type="float")
    }
    _order = 'sequence'
    _defaults = {
        'sequence': 1
    }'''
