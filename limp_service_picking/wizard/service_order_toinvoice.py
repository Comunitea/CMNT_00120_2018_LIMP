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

from openerp.tools.translate import _
from openerp.osv import osv, fields
import time

class service_order_toinvoice(osv.osv_memory):
    _name = 'service.order.toinvoice'

    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')

        vals = []

        value = journal_obj.search(cr, uid, [('type', '=','sale' )])
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            t1 = jr_type.id,jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),
        'group_partner': fields.boolean("Group by partner"),
        'group_building_site': fields.boolean("Group by building site"),
        'invoice_date': fields.date('Invoiced date'),
    }
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(service_order_toinvoice, self).view_init(cr, uid, fields_list, context=context)
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
        res = self.create_invoice(cr, uid, ids, context=context)
        invoice_ids += res.values()
        if not invoice_ids:
            return {}
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

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.service.picking')
        formdata_obj = self.read(cr, uid, ids, ['journal_id', 'group_partner','group_building_site', 'invoice_date'])

        date_inv = formdata_obj[0]['invoice_date'] or time.strftime("%Y-%m-%d")

        journal_id = formdata_obj[0]['journal_id']
        group_partner = formdata_obj[0]['group_partner']
        group_building_site = formdata_obj[0]['group_building_site']


        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices_group = {}
        res = {}

        for service_picking in picking_pool.browse(cr, uid, context.get('active_ids', []), context=context):
            intercompany = False
            if service_picking.invoice_line_ids or service_picking.state <> 'closed' or service_picking.invoice_type == 'noinvoice':
                continue
            key = "del:" + str(service_picking.delegation_id.id) + "/dep:" + str(service_picking.department_id.id) + "/m:" + str(service_picking.manager_id.id)
            payment_term_id = False
            partner = service_picking.partner_id
            building_site = service_picking.building_site_id and service_picking.building_site_id or False
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the service order list if you want to generate invoice.'))

            account_id = partner.property_account_receivable.id
            payment_term_id = service_picking.payment_term.id
            address_contact_id = service_picking.address_id.id
            address_tramit_id = service_picking.address_tramit_id and service_picking.address_tramit_id.id or False
            address_invoice_id = service_picking.address_invoice_id.id
            comment = False

            if service_picking.ccc_account_id:
                key += "bank:" + str(service_picking.ccc_account_id.id)
            if service_picking.fiscal_position:
                key += "fp:" + str(service_picking.fiscal_position.id)
            if service_picking.payment_type:
                key += "ptype:" + str(service_picking.payment_type.id)
            if service_picking.payment_term:
                key += "pterm:" + str(service_picking.payment_term.id)
            if service_picking.intercompany:
                key += "interc:1"

            if service_picking.intercompany:
                if not comment:
                    comment = u"%s: " % service_picking.name
                else:
                    comment += "\n%s: " % service_picking.name
                comment += u"DEL: %s, " % service_picking.invoice_delegation_id.name
                comment += u"DEP: %s, " % service_picking.invoice_department_id.name
                comment += u"RESP: %s\n" % service_picking.invoice_responsible_id.name
                intercompany = True

            if group_building_site and building_site and (key + "b:" + str(building_site.id) + "p:" + str(partner.id)) in invoices_group:
                invoice_id = invoices_group[key + "b:" + str(building_site.id) + "p:" + str(partner.id)]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or u'') + u', ' + (service_picking.name or u''),
                    'origin': (invoice.origin or '') + u', ' + (service_picking.name or u''),
                    'comment': (comment and (invoice.comment and invoice.comment+u"\n"+comment or comment)) or (invoice.comment and invoice.comment or u''),
                    'date_invoice':date_inv or False,
                    'user_id': uid,
                    'intercompany': intercompany
                }
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals, context=context)
            elif group_partner and (key + "p:" + str(partner.id)) in invoices_group:
                invoice_id = invoices_group[key + "p:" + str(partner.id)]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or u'') + u', ' + (service_picking.name or u''),
                    'origin': (invoice.origin or u'') + u', ' + (service_picking.name or u''),
                    'comment': (comment and (invoice.comment and invoice.comment+u"\n"+comment or comment)) or (invoice.comment and invoice.comment or u''),
                    'date_invoice':date_inv or False,
                    'user_id': uid,
                    'intercompany': intercompany
                }
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals, context=context)
            else:
                invoice_vals = {
                    'name': service_picking.name,
                    'origin': (service_picking.name or u'') ,
                    'type': 'out_invoice',
                    'account_id': account_id,
                    'partner_id': partner.id,
                    'address_invoice_id': address_invoice_id,
                    'address_contact_id': address_contact_id,
                    'address_tramit_id': address_tramit_id,
                    'comment': comment,
                    'payment_term': payment_term_id,
                    'partner_bank_id': (service_picking.payment_type and service_picking.payment_type.suitable_bank_types) and (service_picking.ccc_account_id and service_picking.ccc_account_id.id or (partner.bank_ids and partner.bank_ids[0].id or False)) or False,
                    'payment_type': service_picking.payment_type.id,
                    'fiscal_position': service_picking.fiscal_position.id,
                    'date_invoice': date_inv or False,
                    'company_id': service_picking.company_id.id,
                    'user_id': uid,
                    'delegation_id': service_picking.delegation_id.id,
                    'department_id': service_picking.department_id.id,
                    'manager_id': service_picking.manager_id.id,
                    'intercompany': intercompany,
                    'analytic_id': service_picking.analytic_acc_id.id
                }

                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice_id = invoice_obj.create(cr, uid, invoice_vals,
                        context=context)
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                if group_building_site and building_site:
                    invoices_group[key + "b:" + str(building_site.id) + "p:" + str(partner.id)] = invoice_id
                elif group_partner:
                    invoices_group[key + "p:" + str(partner.id)] = invoice_id
            res[service_picking.id] = invoice_id
            for move_line in service_picking.service_invoice_concept_ids:
                if group_partner or group_building_site:
                    name = (service_picking.name or u'') + u'-' + move_line.name
                else:
                    name = move_line.name

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
                    'invoice_id': invoice_id,
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
                    'invoice_id': invoice_id,
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
                    raise osv.except_osv(_('Error!'), _('Income account in product %s is not set') % ervice_picking.product_sand_id.name)

                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                        cr,
                        uid,
                        service_picking.partner_id.property_account_position,
                        service_picking.product_sand_id.taxes_id
                )

                invoice_line_obj.create(cr, uid, {
                    'name': service_picking.product_sand_id.name,
                    'invoice_id': invoice_id,
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

            invoice.button_reset_taxes()
            if intercompany:
                in_journal_ids = self.pool.get('account.journal').search(cr, uid, [('intercompany', '=', True)])
                if not in_journal_ids:
                    raise osv.except_osv(_('Error!'), _('Any income intercompany account journal found.'))

                new_invoice = invoice_obj.copy(cr, uid, invoice_id, default={'type': 'in_invoice',
                                                                             'delegation_id': service_picking.invoice_delegation_id.id,
                                                                             'department_id': service_picking.invoice_department_id.id,
                                                                             'manager_id': service_picking.invoice_responsible_id.id,
                                                                             'comment': False,
                                                                             'journal_id': in_journal_ids[0],
                                                                             'reference': service_picking.name
                                                                             })
                invoice.write({'intercompany_invoice_id': new_invoice})
                invoice_copied = invoice_obj.browse(cr, uid, new_invoice)
                invoice_copied.write({'no_quality': True})
                for line in invoice_copied.invoice_line:
                    line.write({'account_analytic_id': False,
                                'invoice_line_tax_id': [(6, 0, [])],
                                'intercompany_invoice_id': False})
                invoice_copied.button_reset_taxes()

        return res


service_order_toinvoice()
