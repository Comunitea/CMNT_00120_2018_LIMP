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

from osv import osv, fields
from tools.translate import _

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation', change_default=True),
        'department_id': fields.many2one('hr.department', 'Department', change_default=True),
        'manager_id': fields.many2one('hr.employee', 'Responsible', change_default=True, domain=[('responsible', '=', True)])
    }

    _defaults = {
        'department_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).context_department_id.id,
        'delegation_id': lambda s,cr,uid,c: s.pool.get('res.users').browse(cr,uid,uid).context_delegation_id.id,
        'manager_id': lambda self, cr, uid, context: self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0] or False,
    }

    def _get_analytic_lines(self, cr, uid, id):
        acct_ins_obj = self.pool.get('account.analytic.plan.instance')
        cur_obj = self.pool.get('res.currency')
        inv = self.browse(cr, uid, id)
        if not inv.journal_id.analytic_journal_id:
            raise osv.except_osv(_('No Analytic Journal !'),_("You have to define an analytic journal on the '%s' journal!") % (inv.journal_id.name,))
        company_currency = inv.company_id.currency_id.id

        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1
        if inv.type in ('in_invoice', 'in_refund'):
            ref = inv.reference
        else:
            ref = self._convert_ref(cr, uid, inv.number)

        res = self.pool.get('account.invoice.line').move_line_get(cr, uid, inv.id)
        for record in res:
            if record.get('account_analytic_id', False):
                record['analytic_lines'] = [(0,0, {
                    'name': record['name'],
                    'date': inv.date_invoice,
                    'account_id': record['account_analytic_id'],
                    'unit_amount': record['quantity'],
                    'amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, record['price'], context={'date': inv.date_invoice}) * sign,
                    'product_id': record['product_id'],
                    'product_uom_id': record['uos_id'],
                    'general_account_id': record['account_id'],
                    'journal_id': inv.journal_id.analytic_journal_id.id,
                    'ref': ref,
                    'department_id': inv.department_id.id,
                    'delegation_id': inv.delegation_id.id,
                    'manager_id': inv.manager_id.id,
                    'partner_id': inv.partner_id.id
                })]
            elif record.get('analytics_id', False):
                obj_move_line = acct_ins_obj.browse(cr, uid, record['analytics_id'])
                amount_calc = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, record['price'], context={'date': inv.date_invoice}) * sign
                qty = record['quantity']
                record['analytic_lines'] = []
                for line2 in obj_move_line.account_ids:
                    amt = line2.rate and amount_calc * (line2.rate/100) or (line2.fix_amount)
                    qtty = line2.rate and qty* (line2.rate/100) or 1
                    al_vals = {
                        'name': record['name'],
                        'date': inv.date_invoice,
                        'unit_amount': qtty,
                        'product_id': record['product_id'],
                        'account_id': line2.analytic_account_id.id,
                        'amount': amt,
                        'product_uom_id': record['uos_id'],
                        'general_account_id': record['account_id'],
                        'journal_id': obj_move_line.journal_id and obj_move_line.journal_id.id or self._get_journal_analytic(cr, uid, inv.type),
                        'ref': ref,
                        'department_id': line2.department_id.id,
                        'delegation_id': line2.delegation_id.id,
                        'manager_id': line2.manager_id.id,
                        'partner_id': inv.partner_id.id,
                    }
                    record['analytic_lines'].append((0, 0, al_vals))

        return res

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        upd = {}
        if invoice_browse.delegation_id:
            upd['delegation_id'] = invoice_browse.delegation_id.id
        if invoice_browse.department_id:
            upd['department_id'] = invoice_browse.department_id.id
        if invoice_browse.manager_id:
            upd['manager_id'] = invoice_browse.manager_id.id

        for line in move_lines:
            line[2].update(upd)


        return super(account_invoice, self).finalize_invoice_move_lines(cr, uid, invoice_browse, move_lines)


    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None):
        new_ids = super(account_invoice, self).refund(cr, uid, ids, date=date, period_id=period_id, description=description, journal_id=journal_id)
        orig_invoice_obj_id = self.browse(cr, uid, ids[0])
        self.write(cr, uid, new_ids, {
            'department_id': orig_invoice_obj_id.department_id and orig_invoice_obj_id.department_id.id or False,
            'delegation_id': orig_invoice_obj_id.delegation_id and orig_invoice_obj_id.delegation_id.id or False,
            'manager_id': orig_invoice_obj_id.manager_id and orig_invoice_obj_id.manager_id.id or False,
        })

        return new_ids

account_invoice()
