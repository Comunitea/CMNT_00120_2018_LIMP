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

"""Concepts to invoice analytic accounts"""

from openerp.osv import osv, fields
import time
from datetime import datetime
from openerp.tools.translate import _

MONTHS = {
    '1': _("Enero"),
    '2': _("Febrero"),
    '3': _("Marzo"),
    '4': _("Abril"),
    '5': _("Mayo"),
    '6': _("Junio"),
    '7': _("Julio"),
    '8': _('Agosto'),
    '9': _("Septiembre"),
    '10': _("Octubre"),
    '11': _("Noviembre"),
    '12': _("Diciembre")
}

class account_analytic_invoice_concept(osv.osv):
    """Concepts to invoice analytic accounts"""

    _name = "account.analytic.invoice.concept"
    _description = "Analytic account invoice concepts"

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        """allows search by code too"""
        if args is None: args=[]
        if context is None: context={}

        if name:
            ids = self.search(cr, user, [('code', '=', name)]+ args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('code', operator, name)]+ args, limit=limit, context=context)
                ids += self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
                ids = list(set(ids))
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)

        result = self.name_get(cr, user, ids, context)
        return result

    def process_name(self, concept, description=False, date=False):
        """replaces time commands with its correspondent and currently timedata"""
        if not date:
            date = datetime.now()
        if description:
            res = description.replace('%(year)s', str(date.year)).replace('%(month)s', MONTHS[str(date.month)])
        else:
            res = concept.name.replace('%(year)s', str(date.year)).replace('%(month)s', MONTHS[str(date.month)])
        return res

    _columns = {
        'name': fields.char('Concept', size=255, translate=True, required=True),
        'code': fields.char('Code', size=8, required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True, help="Product required to map invoice taxes."),
        'company_id':fields.many2one('res.company','Company',required=True),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id,
    }

account_analytic_invoice_concept()
