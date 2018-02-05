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

class account_analytic_account(models.Model):

    _inherit = "account.analytic.account"

    def _invoice_hook(self, cr, uid, analytic, invoice_id, end_date, context=None):
        if context is None: context = {}

        super(account_analytic_account, self)._invoice_hook(cr, uid, analytic, invoice_id, end_date, context=context)

        line = False
        vals = {}

        home_help_lines = self.pool.get('limp.contract.line.home.help').search(cr, uid, [('analytic_acc_id', '=', analytic.id)])
        if home_help_lines:
            line = self.pool.get('limp.contract.line.home.help').browse(cr, uid, home_help_lines[0])

        cleaning_lines = self.pool.get('limp.contract.line.cleaning').search(cr, uid, [('analytic_acc_id', '=', analytic.id)])
        if cleaning_lines:
            line = self.pool.get('limp.contract.line.cleaning').browse(cr, uid, cleaning_lines[0])

        if line:
            vals = {
                'no_quality': line.contract_id.no_quality,
            }
        else:
            contracts = self.pool.get('limp.contract').search(cr, uid, [('analytic_account_id', '=', analytic.id)])
            if contracts:
                contract = self.pool.get('limp.contract').browse(cr, uid, contracts[0])
                vals = {
                    'no_quality': contract.no_quality,
                }

        self.pool.get('account.invoice').write(cr, uid, [invoice_id], vals, context=context)

        return

    def _invoice_line_hook(self, cr, uid, analytic, concept, invoice_line, end_date, context=None):
        if context is None: context = {}
        line = self.pool.get('account.invoice.line').browse(cr, uid, invoice_line)
        if line.invoice_id and line.invoice_id.no_quality:
            line.write({'invoice_line_tax_id': [(6,0, [])]})

        return super(account_analytic_account, self)._invoice_line_hook(cr, uid, analytic, concept, invoice_line, end_date, context=context)


account_analytic_account()
