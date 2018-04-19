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
from odoo import models, fields


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    contract_id = fields.Many2one('limp.contract', 'Contract', readonly=True)
    invoice_header = fields.Char('Invoice header', size=128)
    privacy = fields.Selection(
        related='analytic_id.privacy', string="Privacy",
        selection=[('public', 'Public'), ('private', 'Private')],
        readonly=True, store=True)

    def refund(self, date_invoice=None, date=None, description=None,
               journal_id=None):
        new_ids = super(AccountInvoice, self).refund(
            date_invoice, date, description, journal_id)
        new_ids.write({
            'contract_id': self.contract_id and self.contract_id.id or False,
            'analytic_id': self.analytic_id and self.analytic_id.id or False
        })

        return new_ids


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    hours = fields.Float('Hours', digits=(16, 2))
