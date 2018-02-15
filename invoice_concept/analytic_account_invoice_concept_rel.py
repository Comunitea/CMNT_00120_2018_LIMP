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

"""Relationship between invoice concepts and analytic accounts"""

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp

class AccountAnalyticInvoiceConceptRel(models.Model):
    """Relationship between invoice concepts and analytic accounts"""

    _name = 'account.analytic.invoice.concept.rel'
    _description = "Relationship between analytic account and invoice concepts"
    _order = "sequence asc"

    concept_id = fields.Many2one('account.analytic.invoice.concept', 'Concept', required=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Account', readonly=True)
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'), required=True)
    freq = fields.Selection([('q', 'Quarterly'), ('m', 'Monthly')], 'Frequency', required=True, default='m')
    last_invoice_date = fields.Date('Last invoice date', copy=False)
    january = fields.Boolean('January', default=True)
    february = fields.Boolean('February', default=True)
    march = fields.Boolean('March', default=True)
    april = fields.Boolean('April', default=True)
    may = fields.Boolean('May', default=True)
    june = fields.Boolean('June', default=True)
    july = fields.Boolean('July', default=True)
    august = fields.Boolean('August', default=True)
    september = fields.Boolean('September', default=True)
    october = fields.Boolean('October', default=True)
    november = fields.Boolean('November', default=True)
    december = fields.Boolean('December', default=True)
    name = fields.Char('Description', default=True)
    sequence = fields.Integer('Sequence', required=True, default=1)

    @api.onchange('concept_id')
    def onchange_concept_id(self):
        for obj in self:
            if obj.concept_id:
                obj.name = obj.concept_id.name

    @api.multi
    def _get_except_months(self):
        """returns list of exception months"""

        res = {}
        for record in self:
            res[record.id] = []
            if not record.january:
                res[record.id].append(1)
            if not record.february:
                res[record.id].append(2)
            if not record.march:
                res[record.id].append(3)
            if not record.april:
                res[record.id].append(4)
            if not record.may:
                res[record.id].append(5)
            if not record.june:
                res[record.id].append(6)
            if not record.july:
                res[record.id].append(7)
            if not record.august:
                res[record.id].append(8)
            if not record.september:
                res[record.id].append(9)
            if not record.october:
                res[record.id].append(10)
            if not record.november:
                res[record.id].append(11)
            if not record.december:
                res[record.id].append(12)

        return res
