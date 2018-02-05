# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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
import netsvc


class remove_no_quality(models.TransientModel):

    _name = "remove.no.quality"

    _columns = {
        'to_date': fields.date('To date', required=True)
    }

    _defaults = {
        'to_date': lambda *a: time.strftime("%Y-%m-%s")
    }

    def delete_no_quality(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0])
        invoice_ids = self.pool.get('account.invoice').search(cr, 1, [('no_quality', '=', True), ('date_invoice', '<=', obj.to_date)])
        invoice_to_unlink = []

        for invoice in self.pool.get('account.invoice').browse(cr, 1, invoice_ids):
            if invoice.state in ('draft', 'cancel'):
                invoice_to_unlink.append(invoice.id)
            elif invoice.state in ('proforma', 'proforma2', 'open'):
                invoice.action_cancel()
                invoice_to_unlink.append(invoice.id)
            elif invoice.state == 'paid':
                other_moves = []
                for line in invoice.move_id.line_id:
                    if line.reconcile_id:
                        for rline in line.reconcile_id.line_id:
                            if rline.id != line.id:
                                other_moves.append(rline.move_id.id)
                        for rline in line.reconcile_id.line_partial_ids:
                            if rline.id != line.id:
                                other_moves.append(rline.move_id.id)
                        line.reconcile_id.unlink()
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(1, 'account.invoice', invoice.id, 'open_test', cr)
                        invoice.action_cancel()
                        invoice_to_unlink.append(invoice.id)
                if other_moves:
                    voucher_ids = self.pool.get('account.voucher').search(cr, 1, [('move_id', 'in', list(set(other_moves)))])
                    voucher_ids = list(set(voucher_ids))
                    if voucher_ids:
                        for voucher_id in voucher_ids:
                            unreconcile_wzd_id = self.pool.get('account.voucher.unreconcile').create(cr, 1, {})
                            self.pool.get('account.voucher.unreconcile').trans_unrec(cr, 1, [unreconcile_wzd_id], context={'active_id': voucher_id})
                        self.pool.get('account.voucher').unlink(cr, 1, voucher_ids)

        self.pool.get('account.invoice').unlink(cr, 1, invoice_to_unlink)

        return {'type': 'ir.actions.act_window_close'}

remove_no_quality()
