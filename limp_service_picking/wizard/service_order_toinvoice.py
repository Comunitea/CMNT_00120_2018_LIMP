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

class ServiceOrderToinvoice(models.TransientModel):
    _name = 'service.order.toinvoice'

    def _get_journal_id(self):
        vals = []
        for jr_type in self.env['account.journal'].search([('type', '=','sale' )]):
            t1 = jr_type.id, jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    journal_id = fields.Selection(_get_journal_id, 'Destination Journal',required=True)
    group_partner = fields.Boolean("Group by partner")
    group_building_site = fields.Boolean("Group by building site")
    invoice_date = fields.Date('Invoiced date')

    def view_init(self, fields_list):
        res = super(ServiceOrderToinvoice, self).view_init(fields_list)
        for pick in self.env['stock.service.picking'].browse(self._context.get('active_ids',[])):
            if pick.state != 'closed' or pick.invoice_line_ids or pick.invoice_type == 'noinvoice':
                raise UserError(_('The service order %s does not prepares to be invoiced or it was already invoiced.') % (pick.name))
        return res

    def open_invoice(self):
        res = self.create_invoice()
        invoice_ids = res.values()
        if not invoice_ids:
            return {}
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['domain'] = "[('id','in', ["+','.join(map(str, invoice_ids))+"])]"
        return action

    def create_invoice(self):
        date_inv = self.invoice_date or fields.Date.today()
        journal_id = int(self.journal_id)
        group_partner = self.group_partner
        group_building_site = self.group_building_site

        invoice_line_obj = self.env['account.invoice.line']
        invoices_group = {}
        res = {}

        for service_picking in self.env['stock.service.picking'].browse(self._context.get('active_ids', [])):
            intercompany = False
            if service_picking.invoice_line_ids or service_picking.state != 'closed' or service_picking.invoice_type == 'noinvoice':
                continue
            key = "del:" + str(service_picking.delegation_id.id) + "/dep:" + str(service_picking.department_id.id) + "/m:" + str(service_picking.manager_id.id)
            payment_term_id = False
            partner = service_picking.partner_id
            fpos = partner.property_account_position_id
            building_site = service_picking.building_site_id and service_picking.building_site_id or False
            if not partner:
                raise UserError(_('Please put a partner on the service order list if you want to generate invoice.'))

            account_id = partner.property_account_receivable_id.id
            payment_term_id = service_picking.payment_mode.id
            address_contact_id = service_picking.address_id.id
            address_tramit_id = service_picking.address_tramit_id and service_picking.address_tramit_id.id or False
            comment = False

            if service_picking.ccc_account_id:
                key += "bank:" + str(service_picking.ccc_account_id.id)
            if service_picking.fiscal_position:
                key += "fp:" + str(service_picking.fiscal_position.id)
            if service_picking.payment_mode:
                key += "ptype:" + str(service_picking.payment_mode.id)
            if service_picking.payment_mode:
                key += "pterm:" + str(service_picking.payment_mode.id)
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
                invoice = invoices_group[key + "b:" + str(building_site.id) + "p:" + str(partner.id)]
                invoice_vals = {
                    'name': (invoice.name or u'') + u', ' + (service_picking.name or u''),
                    'origin': (invoice.origin or '') + u', ' + (service_picking.name or u''),
                    'comment': (comment and (invoice.comment and invoice.comment+u"\n"+comment or comment)) or (invoice.comment and invoice.comment or u''),
                    'date_invoice':date_inv or False,
                    'user_id': self.env.user.id,
                    'intercompany': intercompany
                }
                invoice.write(invoice_vals)
            elif group_partner and (key + "p:" + str(partner.id)) in invoices_group:
                invoice = invoices_group[key + "p:" + str(partner.id)]
                invoice_vals = {
                    'name': (invoice.name or u'') + u', ' + (service_picking.name or u''),
                    'origin': (invoice.origin or u'') + u', ' + (service_picking.name or u''),
                    'comment': (comment and (invoice.comment and invoice.comment+u"\n"+comment or comment)) or (invoice.comment and invoice.comment or u''),
                    'date_invoice':date_inv or False,
                    'user_id': self.env.user.id,
                    'intercompany': intercompany
                }
                invoice.write(invoice_vals)
            else:
                invoice_vals = {
                    'name': service_picking.name,
                    'origin': (service_picking.name or u'') ,
                    'type': 'out_invoice',
                    'account_id': account_id,
                    'partner_id': partner.id,
                    'partner_shipping_id': address_contact_id,
                    'address_tramit_id': address_tramit_id,
                    'comment': comment,
                    'payment_mode_id': payment_term_id,
                    'payment_mode_id': service_picking.payment_mode.id,
                    'fiscal_position_id': service_picking.fiscal_position.id,
                    'date_invoice': date_inv or False,
                    'company_id': service_picking.company_id.id,
                    'user_id': self.env.user.id,
                    'delegation_id': service_picking.delegation_id.id,
                    'department_id': service_picking.department_id.id,
                    'manager_id': service_picking.manager_id.id,
                    'intercompany': intercompany,
                    'analytic_id': service_picking.analytic_acc_id.id
                }

                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice = self.env['account.invoice'].create(invoice_vals)
                if group_building_site and building_site:
                    invoices_group[key + "b:" + str(building_site.id) + "p:" + str(partner.id)] = invoice
                elif group_partner:
                    invoices_group[key + "p:" + str(partner.id)] = invoice
            res[service_picking.id] = invoice.id
            for move_line in service_picking.service_invoice_concept_ids:
                if group_partner or group_building_site:
                    name = (service_picking.name or u'') + u'-' + move_line.name
                else:
                    name = move_line.name

                account_id = move_line.product_id.product_tmpl_id.\
                            property_account_income_id
                if not account_id:
                    account_id = move_line.product_id.categ_id.\
                            property_account_income_categ_id

                if not account_id:
                    raise UserError(_('Income account in product %s is not set') % move_line.product_id.name)

                price_unit = move_line.price
                tax_ids = fpos.map_tax(move_line.product_id.taxes_id)._ids
                account_id = fpos.map_account(account_id).id

                invoice_line_id = invoice_line_obj.create({
                    'name': name,
                    'invoice_id': invoice.id,
                    'product_id': move_line.product_id.id,
                    'uom_id': move_line.product_uom and move_line.product_uom.id or move_line.product_id.uom_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'quantity': move_line.product_qty,
                    'invoice_line_tax_ids': [(6, 0, tax_ids)],
                    'building_site_id': service_picking.building_site_id and service_picking.building_site_id.id or False,
                    'account_analytic_id': service_picking.analytic_acc_id.id,
                    'service_picking_id': service_picking.id
                })
            service_picking.write({'invoice_type': 'invoiced'})

            if service_picking.taxes:
                if not service_picking.product_tax_id:
                    raise UserError(_('Product tax is not set in picking %s') % service_picking.name)

                account_id = service_picking.product_tax_id.product_tmpl_id.\
                            property_account_income
                if not account_id:
                    account_id = service_picking.product_tax_id.categ_id.\
                            property_account_income_categ

                if not account_id:
                    raise UserError(_('Income account in product %s is not set') % service_picking.product_tax_id.name)

                tax_ids = fpos.map_tax(service_picking.product_tax_id.taxes_id)._ids

                invoice_line_obj.create({
                    'name': service_picking.product_tax_id.name,
                    'invoice_id': invoice.id,
                    'product_id': service_picking.product_tax_id.id,
                    'uom_id': service_picking.product_tax_id.uom_id.id,
                    'account_id': fpos.map_account(account_id).id,
                    'price_unit': service_picking.taxes,
                    'quantity': 1.0,
                    'invoice_line_tax_ids': [(6, 0, tax_ids)],
                    'building_site_id': service_picking.building_site_id and service_picking.building_site_id.id or False,
                    'account_analytic_id': service_picking.analytic_acc_id.id,
                    'service_picking_id': service_picking.id
                })

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

                tax_ids = fpos.map_tax(service_picking.product_sand_id.taxes_id)._ids

                invoice_line_obj.create({
                    'name': service_picking.product_sand_id.name,
                    'invoice_id': invoice.id,
                    'product_id': service_picking.product_sand_id.id,
                    'uom_id': service_picking.product_sand_id.uom_id.id,
                    'account_id': fpos.map_account(account_id).id,
                    'price_unit': service_picking.sand_amount,
                    'quantity': 1.0,
                    'invoice_line_tax_ids': [(6, 0, tax_ids)],
                    'building_site_id': service_picking.building_site_id and service_picking.building_site_id.id or False,
                    'account_analytic_id': service_picking.analytic_acc_id.id,
                    'service_picking_id': service_picking.id
                })

            invoice.compute_taxes()
            if intercompany:
                in_journal_ids = self.env['account.journal'].search([('intercompany', '=', True)])
                if not in_journal_ids:
                    raise UserError(_('Any income intercompany account journal found.'))

                invoice_copied = invoice.copy(
                    default={'type': 'in_invoice',
                             'delegation_id': service_picking.invoice_delegation_id.id,
                             'department_id': service_picking.invoice_department_id.id,
                             'manager_id': service_picking.invoice_responsible_id.id,
                             'comment': False,
                             'journal_id': in_journal_ids[0],
                             'reference': service_picking.name
                            })
                invoice.write({'intercompany_invoice_id': invoice_copied.id})
                invoice_copied.write({'no_quality': True})
                invoice_copied.invoice_line.write(
                    {'account_analytic_id': False,
                     'invoice_line_tax_ids': [(6, 0, [])],
                     'intercompany_invoice_id': False})
                invoice_copied.compute_taxes()

        return res
