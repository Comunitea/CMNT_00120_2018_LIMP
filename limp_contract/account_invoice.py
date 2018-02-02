# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'contract_id': fields.many2one('limp.contract', 'Contract', readonly=True),
        'invoice_header': fields.char('Invoice header', size=128),
        'privacy': fields.related('analytic_id', 'privacy', type="selection", string="Privacy", selection=[('public', 'Public'), ('private', 'Private')], readonly=True)
    }

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None):
        new_ids = super(account_invoice, self).refund(cr, uid, ids, date=date, period_id=period_id, description=description, journal_id=journal_id)
        orig_invoice_obj_id = self.browse(cr, uid, ids[0])
        self.write(cr, uid, new_ids, {
            'contract_id': orig_invoice_obj_id.contract_id and orig_invoice_obj_id.contract_id.id or False,
            'analytic_id': orig_invoice_obj_id.analytic_id and orig_invoice_obj_id.analytic_id.id or False
        })

        return new_ids

account_invoice()

class account_invoice_line(osv.osv):

     _inherit = "account.invoice.line"

     _columns = {
        'hours': fields.float('Hours', digits=(16,2))
     }

account_invoice_line()
