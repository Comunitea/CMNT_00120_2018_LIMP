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

from osv import osv, fields
import decimal_precision as dp
from datetime import datetime,timedelta

class sale_order(osv.osv):

    _inherit = 'sale.order'
    _order = "date_order desc"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
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
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()


    _columns = {
        #'freq_table': fields.text('Frequency table'),
        'periodicity_id': fields.many2one('sale.order.periodicity', 'Periodicity', help="Multiply total amount by periodicity value"),
        'delegation_id': fields.many2one('res.delegation', 'Delegation', required=True, change_default=True),
        'department_id': fields.many2one('hr.department', 'Department', required=True, change_default=True),
        'center_type_id': fields.many2one("limp.center.type", "Center type", change_default=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','periodicity_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','periodicity_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','periodicity_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'margin': fields.function(_amount_all, method=True, digits_compute = dp.get_precision('Sale Price'), string='Margin',
            help='It gives profitability by calculating the difference between the Unit Price and Cost Price of Prices rules.',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','periodicity_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10)
            },
            multi='sums'),
        'margin_percentage': fields.function(_amount_all, method=True, string='Profitability (%)', type="float", digits_compute = dp.get_precision('Sale Price'),
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','periodicity_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10)
            }, multi="sums"),
        'contract_ids': fields.one2many('limp.contract', 'sale_id', string="Contracts", readonly=True),
        'created_contract': fields.boolean('Created contract', readonly=True),
        'created_service_order': fields.boolean('Created Service order', readonly=True),
        'created_service_pick': fields.boolean('Created Service pick', readonly=True),
        'service_order_ids': fields.one2many('waste.service', 'sale_id', string='Service orders', readonly=True),
        'task_frequency_ids': fields.one2many('task.frequency', 'sale_id', 'Task Frequency'),
        'validity_date': fields.date('End of validity'),
        'very_important_text': fields.text('Very important'),
        'header_notes': fields.text('Header notes'),
        'show_total': fields.boolean("Show total in report")
    }
    _defaults = {
        #'freq_table': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).freq_table,
        # 'department_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).context_department_id.id, MIGRACION: El campo context_department_id no existe
        'delegation_id': lambda s, cr, uid, c: s.pool.get('res.users').browse(cr, uid, uid).context_delegation_id.id,
        'name': lambda *a: "/",
        'show_total': lambda *a: True,
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', False) == "/":
            vals["name"] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order')
        if not vals.get('validity_date', False):
            formatted_date = datetime.strptime(vals['date_order'], "%Y-%m-%d")
            vals['validity_date'] = datetime.strftime(formatted_date + timedelta(days=30),"%Y-%m-%d")
        return super(sale_order, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'created_contract' : False,
            'created_service_order': False,
            'created_service_pick': False,
            'service_order_ids': [],
            'contract_ids': [],
            'validity_date': False
        })

        return super(sale_order, self).copy(cr, uid, id, default, context)


    def get_all_tasks(self, cr, uid, ids, context=None):
        """Load all task related with this sale order"""
        if context is None: context = {}

        for line in self.browse(cr, uid, ids):
            if not line.department_id:
                raise osv.except_osv(_('Error!'), _('Not department defined for this sale order'))
            task_ids = self.pool.get('limp.contract.task').search(cr, uid, ['|',('department_id', '=', line.department_id.id), ('department_id', '=', False),'|',('center_type_id','=',line.center_type_id.id),('center_type_id','=',False)])
            for task in self.pool.get('limp.contract.task').browse(cr, uid, task_ids):
                self.pool.get('task.frequency').create(cr, uid, {'task_id': task.id, 'sale_id': line.id, 'sequence': task.sequence})

        return True

    def action_ship_create(self, cr, uid, ids, *args):
        res = super(sale_order, self).action_ship_create(cr, uid, ids, args)

        for order in self.browse(cr, uid, ids):
            if order.order_policy != 'picking':
                picking_ids = self.pool.get('stock.picking').search(cr, uid, [('sale_id', '=', order.id)])
                if picking_ids:
                    move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', picking_ids)])
                    self.pool.get('stock.picking').write(cr, uid, picking_ids, {'state': 'draft'})
                    self.pool.get('stock.move').write(cr, uid, move_ids, {'state': 'draft', 'picking_id': False})
                    self.pool.get('stock.move').unlink(cr, uid, move_ids)
                    self.pool.get('stock.picking').unlink(cr, uid, picking_ids)

        return res

    def create_contract(self, cr, uid, ids, context=None):
        if context is None: context = {}

        sale = self.browse(cr, uid, ids[0])
        contract_id = self.pool.get('limp.contract').create(cr, uid, {
            'company_id': sale.company_id.id,
            'delegation_id': sale.delegation_id.id,
            'department_id': sale.department_id.id,
            'partner_id': sale.partner_id.id,
            'amount': sale.amount_total,
            'address_id': sale.partner_shipping_id.id,
            'bank_account_id': sale.partner_bank and sale.partner_bank.id or False,
            'payment_term_id': sale.payment_term and sale.payment_term.id or False,
            'payment_type_id': sale.payment_type and sale.payment_type.id or False,
            'address_invoice_id': sale.partner_invoice_id.id,
            'sale_id': sale.id
        })

        sale.write({'created_contract': True})

        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'limp_contract', 'limp_contract_form')
        res_id = res and res[1] or False,

        return {
            'name': 'Contract',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'limp.contract',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': contract_id,
        }
    def create_service_order(self, cr, uid, ids, context=None):
        if context is None: context = {}
        sale = self.browse(cr, uid, ids[0])
        vals = {
            'partner_id': sale.partner_id.id,
            'contact_id': sale.partner_order_id.id,
            'address_invoice_id': sale.partner_invoice_id.id,
            'company_id': sale.company_id.id,
            'partner_shipping_id': sale.partner_shipping_id.id,
            'sale_id': sale.id,
            'pricelist_id': sale.pricelist_id.id,
            'payment_term': sale.payment_term and sale.payment_term.id or False,
            'payment_type': sale.payment_type and sale.payment_type.id or False,
            'partner_bank_id': sale.partner_bank and sale.partner_bank.id or False,
            'fiscal_position': sale.fiscal_position and sale.fiscal_position.id or False
        }
        service_order_id = self.pool.get('waste.service').create(cr, uid, vals)
        sale.write({'created_service_order': True})

        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'limp_service_picking', 'waste_service_form')
        res_id = res and res[1] or False

        return {
            'name': 'Service order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'waste.service',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': service_order_id
        }

    def create_pick(self, cr, uid, ids, context=None):
        if context is None: context = {}
        sale = self.browse(cr, uid, ids[0])
        vals = {
            'partner_id': sale.partner_id.id,
            'address_id': sale.partner_order_id.id,
            'contact_id': sale.partner_order_id.id,
            'address_invoice_id': sale.partner_invoice_id.id,
            'company_id': sale.company_id.id,
            'partner_shipping_id': sale.partner_shipping_id.id,
            'sale_id': sale.id,
            'picking_type': context['picking_type'],
            'pricelist_id': sale.pricelist_id.id,
            'payment_term': sale.payment_term and sale.payment_term.id or False,
            'payment_type': sale.payment_type and sale.payment_type.id or False,
            'partner_bank_id': sale.partner_bank and sale.partner_bank.id or False,
            'fiscal_position': sale.fiscal_position and sale.fiscal_position.id or False,
            'delegation_id': sale.delegation_id.id,
            'department_id': sale.department_id.id
        }
        if context['picking_type'] == "maintenance":
            vals["maintenance"] = True
            vals["picking_type"] = "sporadic"
        service_pick_id = self.pool.get('stock.service.picking').create(cr, uid, vals)
        sale.write({'created_service_pick': True})

        if context['picking_type'] == 'wastes':
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'limp_service_picking', 'stock_service_picking_form')
        else:
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'limp_service_picking', 'stock_sporadic_service_picking_form')
        res_id = res and res[1] or False

        return {
            'name': 'Service picking',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'stock.service.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': service_pick_id
        }

sale_order()

class sale_order_line(osv.osv):
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
    }


    def product_id_change2(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, address_id=False):

        result = self.product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag)
        price = 0
        purchase_price = 0
        if product and address_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            address_obj = self.pool.get('res.partner.address').browse(cr, uid, address_id)

            rules = product_obj.price_rule_ids
            price = product_obj.list_price
            global_rules = [x for x in rules if not x.province]
            if address_obj.state_id:
                state_rules = [x for x in rules if x.province and x.province.id == address_obj.state_id.id]
            else:
                state_rules = []

            for rule in state_rules or global_rules:
                if qty >= rule.range:
                    price = rule.price
                    purchase_price = rule.cost_price

        if pricelist:
            pricelist_price = self.pool.get('product.pricelist').apply_pricelist_to_price(cr, uid, [pricelist], price, product, qty)
            if pricelist_price:
                price = pricelist_price

            frm_cur = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
            to_cur = self.pool.get('product.pricelist').browse(cr, uid, [pricelist])[0].currency_id.id
            if product and not purchase_price:
                purchase_price = self.pool.get('product.product').browse(cr, uid, product).standard_price
            purchase_price = self.pool.get('res.currency').compute(cr, uid, frm_cur, to_cur, purchase_price, round=False)
            if result.get('value', False):
                result['value'].update({'purchase_price': purchase_price})
            else:
                result['value'] = {'purchase_price': purchase_price}

            if price:
                if result.get('value', False):
                    result['value'].update({'price_unit': price})
                else:
                    result['value'] = {'price_unit': price}

        return result

sale_order_line()
