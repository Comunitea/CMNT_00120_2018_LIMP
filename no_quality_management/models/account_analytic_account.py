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
from odoo import models, fields

class AccountAnalyticAccount(models.Model):

    _inherit = "account.analytic.account"

    def _invoice_hook(self, invoice_id, end_date):
        super(AccountAnalyticAccount, self)._invoice_hook(invoice_id, end_date)

        line = False
        vals = {}

        home_help_lines = self.env['limp.contract.line.home.help'].search([('analytic_acc_id', '=', analytic.id)], limit=1)
        if home_help_lines:
            line = home_help_lines

        cleaning_lines = self.env['limp.contract.line.cleaning'].search([('analytic_acc_id', '=', analytic.id)], limit=1)
        if cleaning_lines:
            line = cleaning_lines

        if line:
            vals = {
                'no_quality': line.contract_id.no_quality,
            }
        else:
            contracts = self.env['limp.contract'].search([('analytic_account_id', '=', analytic.id)], limit=1)
            if contracts:
                vals = {
                    'no_quality': contracts.no_quality,
                }
        self.env['account.invoice'].browse(invoice_id).write(vals)
        return

    def _invoice_line_hook(self, concept, invoice_line, end_date):
        if invoice_line.invoice_id and invoice_line.invoice_id.no_quality:
            invoice_line.write({'invoice_line_tax_id': [(6,0, [])]})
        return super(AccountAnalyticAccount, self)._invoice_line_hook(concept, invoice_line, end_date)
