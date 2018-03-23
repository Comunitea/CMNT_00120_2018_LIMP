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
from odoo import models, fields, _, api
from odoo.exceptions import UserError

class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    no_quality = fields.Boolean('Scont')

    def action_move_create(self):
        for inv in self:
            if inv.no_quality and not inv.journal_id.no_quality:
                raise UserError(_('You try to open scont invoice on not scont journal.'))
            elif not inv.no_quality and inv.journal_id.no_quality:
                raise UserError(_('You try to open normal invoice on scont journal.'))
        return super(AccountInvoice, self).action_move_create()

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('no_quality', False):
            if res.invoice_line_ids:
                res.invoice_line_ids.write({'invoice_line_tax_ids': [(6,0, [])]})
            if res.tax_line_ids:
                res.tax_line_ids.unlink()

        return res

    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if vals.get('no_quality', False):
            for invoice in self:
                if invoice.invoice_line_ids:
                    invoice.invoice_line_ids.write({'invoice_line_tax_ids': [(6,0, [])]})
                if invoice.tax_line_ids:
                    invoice.tax_line_ids.unlink()
        return res
