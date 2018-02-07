# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) Comunitea Servicios Informáticos. All Rights Reserved
#    #Carlos Lombardía Rodríguez carlos@comunitea.com#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class account_analytic_account(osv.osv):
    _name = "account.analytic.account"
    _inherit = "account.analytic.account"

    def get_date_last_invoice(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for acc_id in ids:
            acc_an_line_ids = self.pool.get('account.analytic.line').search(cr, uid, [('account_id', '=', acc_id),('move_id.invoice','!=',False)], order="date desc", limit=1)
            if acc_an_line_ids:
                acc_an_line_id = self.pool.get('account.analytic.line').browse(cr, uid, acc_an_line_ids[0])
                res[acc_id] = acc_an_line_id.date
            else:
                res[acc_id] = ""
        return res


    _columns ={
        'last_invoice_date': fields.function(get_date_last_invoice, method=True, type='date', string='Last Invoice Date',
            help="Date of the last invoice created for this analytic account.")
    }

account_analytic_account()

class account_analytic_line(osv.osv):
    _name ="account.analytic.line"
    _inherit = "account.analytic.line"

    def _get_type_analytic(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.remuneration_id:
                res[line.id] = line.remuneration_id.incidence_id_tp.name
            elif line.timesheet_id:
                res[line.id] = _("Timesheet")
            else:
                res[line.id] = False
        return res

    _columns = {
        'type_analytic': fields.function(_get_type_analytic, method=True, string="Type", readonly=True, type="char", size=50, store={'account.analytic.line': (lambda self, cr, uid, ids, c={}: ids, ['remuneration_id','timesheet_id'], 10)}),
        'privacy': fields.related('account_id', 'privacy', string="Privacy", type="selection", selection=[('public', 'Public'), ('private', 'Private')], readonly=True)
    }

account_analytic_line()
