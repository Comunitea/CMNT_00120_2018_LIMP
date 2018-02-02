# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from tools.translate import _

class add_to_invoice(osv.osv_memory):

    _name = "add.to.invoice"

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True)
    }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(add_to_invoice, self).view_init(cr, uid, fields_list, context=context)
        cur_obj = self.pool.get('stock.service.picking')

        active_ids = context.get('active_ids',[])
        for pick in cur_obj.browse(cr, uid, active_ids, context=context):
            if pick.state <> 'closed' or pick.invoice_line_ids != [] or pick.invoice_type == 'noinvoice':
                raise osv.except_osv(_('Warning !'), _('The service order %s does not prepares to be invoiced or it was already invoiced.') % (pick.name))
        return res

    def open_invoice(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        invoice_ids = []
        data_pool = self.pool.get('ir.model.data')
        invoice_ids = self.add_to_invoice(cr, uid, ids, context=context)
        action_model = False
        action = {}
        action_model = False
        if not invoice_ids:
            raise osv.except_osv(_('Error'), _('No Invoices were created'))
        action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
        return action

    def add_to_invoice(self, cr, uid, ids, context=None):
        if context is None: context = {}

        picking_pool = self.pool.get('stock.service.picking')
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        obj = self.browse(cr, uid, ids[0])
        for service_picking in picking_pool.browse(cr, uid, context.get('active_ids', []), context=context):
            comment = False
            partner = service_picking.partner_id
            invoice_vals = {
                'name': (obj.invoice_id.name or u'') + u', ' + (service_picking.name or u''),
                'origin': (obj.invoice_id.origin or '') + u', ' + (service_picking.name or u''),
                'comment': (comment and (obj.invoice_id.comment and obj.invoice_id.comment+u"\n"+comment or comment)) or (obj.invoice_id.comment and obj.invoice_id.comment or u''),
            }
            invoice_obj.write(cr, uid, [obj.invoice_id.id], invoice_vals, context=context)

            for move_line in service_picking.service_invoice_concept_ids:
                name = (service_picking.name or u'') + u'-' + move_line.name
                account_id = move_line.product_id.product_tmpl_id.\
                            property_account_income.id
                if not account_id:
                    account_id = move_line.product_id.categ_id.\
                            property_account_income_categ.id
                if not account_id:
                    raise osv.except_osv(_('Error!'), _('Income account in product %s is not set') % move_line.product_id.name)

                price_unit = move_line.price
                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                        cr,
                        uid,
                        service_picking.partner_id.property_account_position,
                        move_line.product_id.taxes_id
                )


                account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id)
                invoice_line_id = invoice_line_obj.create(cr, uid, {
                    'name': name,
                    'invoice_id': obj.invoice_id.id,
                    'product_id': move_line.product_id.id,
                    'uos_id': move_line.product_uom and move_line.product_uom.id or move_line.product_id.uom_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'quantity': move_line.product_qty,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'building_site_id': service_picking.building_site_id and service_picking.building_site_id.id or False,
                    'account_analytic_id': service_picking.analytic_acc_id.id,
                    'service_picking_id': service_picking.id
                }, context=context)
            service_picking.write({'invoice_type': 'invoiced'})

            if service_picking.taxes:
                if not service_picking.product_tax_id:
                    raise osv.except_osv(_('Error!'), _('Product tax is not set in picking %s') % service_picking.name)

                account_id = service_picking.product_tax_id.product_tmpl_id.\
                            property_account_income.id
                if not account_id:
                    account_id = service_picking.product_tax_id.categ_id.\
                            property_account_income_categ.id
                if not account_id:
                    raise osv.except_osv(_('Error!'), _('Income account in product %s is not set') % service_picking.product_tax_id.name)

                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                        cr,
                        uid,
                        service_picking.partner_id.property_account_position,
                        service_picking.product_tax_id.taxes_id
                )

                invoice_line_obj.create(cr, uid, {
                    'name': service_picking.product_tax_id.name,
                    'invoice_id': obj.invoice_id.id,
                    'product_id': service_picking.product_tax_id.id,
                    'uos_id': service_picking.product_tax_id.uom_id.id,
                    'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id),
                    'price_unit': service_picking.taxes,
                    'quantity': 1.0,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'building_site_id': service_picking.building_site_id and service_picking.building_site_id.id or False,
                    'account_analytic_id': service_picking.analytic_acc_id.id,
                    'service_picking_id': service_picking.id
                }, context=context)

            if service_picking.sand_amount:
                if not service_picking.product_sand_id:
                    raise osv.except_osv(_('Error!'), _('Product sand treatment is not set in picking %s') % service_picking.name)

                account_id = service_picking.product_sand_id.product_tmpl_id.\
                            property_account_income.id
                if not account_id:
                    account_id = service_picking.product_sand_id.categ_id.\
                            property_account_income_categ.id
                if not account_id:
                    raise osv.except_osv(_('Error!'), _('Income account in product %s is not set') % service_picking.product_sand_id.name)


                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                        cr,
                        uid,
                        service_picking.partner_id.property_account_position,
                        service_picking.product_sand_id.taxes_id
                )

                invoice_line_obj.create(cr, uid, {
                    'name': service_picking.product_sand_id.name,
                    'invoice_id': obj.invoice_id.id,
                    'product_id': service_picking.product_sand_id.id,
                    'uos_id': service_picking.product_sand_id.uom_id.id,
                    'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id),
                    'price_unit': service_picking.sand_amount,
                    'quantity': 1.0,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'building_site_id': service_picking.building_site_id and service_picking.building_site_id.id or False,
                    'account_analytic_id': service_picking.analytic_acc_id.id,
                    'service_picking_id': service_picking.id
                }, context=context)

            obj.invoice_id.button_reset_taxes()

        return [obj.invoice_id.id]

add_to_invoice()
