# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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

from openerp import models, fields
import time

class account_analytic_default(models.Model):

    _inherit = "account.analytic.default"

    _columns = {
        'inv_type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type'),
    }

    def account_get(self, cr, uid, product_id=None, partner_id=None, user_id=None, date=None, inv_type=None, context=None):
        if context is None: context = {}
        domain = []
        if context.get('inv_type'):
            domain += ['|', ('inv_type', '=', context['inv_type'])]
        domain += [('inv_type','=', False)]
        if product_id:
            domain += ['|', ('product_id', '=', product_id)]
        domain += [('product_id','=', False)]
        if partner_id:
            domain += ['|', ('partner_id', '=', partner_id)]
        domain += [('partner_id', '=', False)]
        if user_id:
            domain += ['|',('user_id', '=', user_id)]
        domain += [('user_id','=', False)]
        if date:
            domain += ['|', ('date_start', '<=', date), ('date_start', '=', False)]
            domain += ['|', ('date_stop', '>=', date), ('date_stop', '=', False)]
        best_index = -1
        res = False
        for rec in self.browse(cr, uid, self.search(cr, uid, domain, context=context), context=context):
            index = 0
            if rec.product_id: index += 1
            if rec.partner_id: index += 1
            if rec.user_id: index += 1
            if rec.date_start: index += 1
            if rec.date_stop: index += 1
            if rec.inv_type: index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res

account_analytic_default()

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    _description = "Invoice Line"

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None):
        if context is None: context = {}
        res_prod = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, address_invoice_id, currency_id=currency_id, context=context)
        context['inv_type'] = type
        rec = self.pool.get('account.analytic.default').account_get(cr, uid, product, partner_id, uid, time.strftime('%Y-%m-%d'), context=context)
        if rec:
            if rec.analytics_id:
                res_prod['value'].update({'analytics_id': rec.analytics_id.id})
            elif rec.analytic_id:
                res_prod['value'].update({'account_analytic_id': rec.analytic_id.id})
            else:
                res_prod['value'].update({'account_analytic_id': False})
        else:
            res_prod['value'].update({'account_analytic_id': False})
        return res_prod

account_invoice_line()
