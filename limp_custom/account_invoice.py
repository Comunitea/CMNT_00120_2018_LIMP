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

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp

class account_invoice_line(osv.osv):

    _inherit = "account.invoice.line"

    _columns = {
        'tax_product': fields.related('product_id', 'tax_product', string='Tax product', readonly=True, type="booolean")
    }

account_invoice_line()

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def _amount_taxes(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] =  0.0
            for line in invoice.invoice_line:
                if line.tax_product:
                    res[invoice.id] += line.price_subtotal
        return res

    def _convert_ref(self, cr, uid, ref):
        return ref and (u"FACT. " + ref) or ref

    _columns = {
        'add_info':fields.related('partner_id', 'add_info', string="Additional Information", readonly=True, type="boolean"),
        'amount_taxes': fields.function(_amount_taxes, method=True, digits_compute=dp.get_precision('Account'), string='Tax amount'),
        # 'address_contact_id': fields.many2one('res.partner', 'Contact Address') MIGRACION: Este campo ya no existe
    }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        if res.get('value', False) and res['value'].get('partner_bank_id', False):
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', res['value']['partner_bank_id']), ('state', '=', 'valid')])
            res['value']['sdd_mandate_id'] = mandate_ids and mandate_ids[0] or False

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        invoice_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        if vals.get('partner_bank_id', False) and not vals.get('sdd_mandate_id', False):
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', vals['partner_bank_id']), ('state', '=', 'valid')])
            if mandate_ids:
                self.write(cr, uid, [invoice_id], {
                    'sdd_mandate_id': mandate_ids[0]
                })

        return invoice_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if vals.get('partner_bank_id', False) and not vals.get('sdd_mandate_id', False):
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', vals['partner_bank_id']), ('state', '=', 'valid')])
            if mandate_ids:
                vals['sdd_mandate_id'] = mandate_ids[0]
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

    def onchange_partner_bank(self, cr, uid, ids, partner_bank_id=False):
        res = super(account_invoice, self).onchange_partner_bank(cr, uid, ids, partner_bank_id=partner_bank_id)
        if partner_bank_id:
            mandate_ids = self.pool.get('sdd.mandate').search(cr, uid, [('partner_bank_id', '=', partner_bank_id), ('state', '=', 'valid')])
            if mandate_ids:
                res['value']['sdd_mandate_id'] = mandate_ids[0]
            else:
                res['value']['sdd_mandate_id'] = False
        else:
            res['value']['sdd_mandate_id'] = False

        return res

account_invoice()
