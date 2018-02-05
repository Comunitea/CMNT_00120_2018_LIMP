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

from openerp import models, fields
import decimal_precision as dp

class account_analytic_invoice_concept_rel(models.Model):
    """Relationship between invoice concepts and analytic accounts"""

    _name = 'account.analytic.invoice.concept.rel'
    _description = "Relationship between analytic account and invoice concepts"
    _order = "sequence asc"

    _columns = {
        'concept_id': fields.many2one('account.analytic.invoice.concept', 'Concept', required=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Account', readonly=True),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'), required=True),
        'freq': fields.selection([('q', 'Quarterly'), ('m', 'Monthly')], 'Frequency', required=True),
        'last_invoice_date': fields.date('Last invoice date',),
        'january': fields.boolean('January'),
        'february': fields.boolean('February'),
        'march': fields.boolean('March'),
        'april': fields.boolean('April'),
        'may': fields.boolean('May'),
        'june': fields.boolean('June'),
        'july': fields.boolean('July'),
        'august': fields.boolean('August'),
        'september': fields.boolean('September'),
        'october': fields.boolean('October'),
        'november': fields.boolean('November'),
        'december': fields.boolean('December'),
        'name': fields.char('Description', size=255),
        'sequence': fields.integer('Sequence', required=True)
    }

    def onchange_concept_id(self, cr, uid, ids, concept_id = False):
        if concept_id:
            concept_obj = self.pool.get('account.analytic.invoice.concept').browse(cr, uid, concept_id)
            vals = {}
            vals['name'] = concept_obj.name

            return {'value': vals}

        return {}


    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'last_invoice_date': False})
        return super(account_analytic_invoice_concept_rel, self).copy_data(cr, uid, id, default, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'last_invoice_date': False})

        return super(account_analytic_invoice_concept_rel, self).copy(cr, uid, id, default, context)

    def _get_except_months(self, cr, uid, ids, context=None):
        """returns list of exception months"""
        if context is None: context = {}

        res = {}
        for record in self.browse(cr, uid, ids):
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

    _defaults = {
        'freq': 'm',
        'amount': 0.0,
        'january': True,
        'february': True,
        'march': True,
        'april': True,
        'may': True,
        'june': True,
        'july': True,
        'august': True,
        'september': True,
        'october': True,
        'november': True,
        'december': True,
        'sequence': 1
    }

account_analytic_invoice_concept_rel()
