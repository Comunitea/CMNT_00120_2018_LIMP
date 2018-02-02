# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class stock_picking(osv.osv):

    _inherit = "stock.picking"

    _columns = {
        'invoice_state': fields.selection([
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")], "Invoice Control",
            select=True, required=True),
        'internal_notes': fields.text("Internal Notes")
    }

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        if picking.address_id and not picking.sale_id and not picking.purchase_id:
            vals = {
                'payment_type': picking.address_id.partner_id.payment_type_customer and picking.address_id.partner_id.payment_type_customer.id or False,
            }
            if picking.address_id.partner_id.payment_type_customer and picking.address_id.partner_id.payment_type_customer.suitable_bank_types:
                bank_types = [bt.code for bt in picking.address_id.partner_id.payment_type_customer.suitable_bank_types]
                args = [('partner_id', '=', picking.address_id.partner_id.id), ('state', 'in', bank_types)]
                bank_account_ids = self.pool.get('res.partner.bank').search(cr, uid, args)
                if bank_account_ids:
                    vals['partner_bank_id'] = bank_account_ids[0]

            self.pool.get('account.invoice').write(cr, uid, [invoice_id], vals)

        return super(stock_picking, self)._invoice_hook(cr, uid, picking, invoice_id)

stock_picking()
