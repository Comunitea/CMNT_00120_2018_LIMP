# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api

class StockServiceOtherExpenses(models.Model):

    _name = "stock.service.other.expenses"

    name = fields.Char('Description', required=True, size=255)
    prod_qty = fields.Float('Qty.', digits=(16,2), required=True)
    price_unit = fields.Float('Price unit', required=True)
    price_subtotal = fields.Float('Subtotal', digits=(16, 2), compute='_get_subtotal', store=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic')

    @api.depends('price_unit', 'prod_qty')
    def _get_subtotal(self):
        for expense in self:
            expense.price_subtotal = expense.price_unit * expense.prod_qty
