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

"""Add new no-generic fields"""

from openerp import models, fields
import decimal_precision as dp

class account_analytic_invoice_concept(models.Model):

    _inherit = "account.analytic.invoice.concept"

    _columns = {
        'name': fields.char('Concept', size=255, required=True),
    }

account_analytic_invoice_concept()

class analytic_account_invoice_concept_rel(models.Model):
    """Add new no-generic fields"""

    _inherit = "account.analytic.invoice.concept.rel"

    _columns = {
        'holyday_amount': fields.float('Holyday amount', digits_compute=dp.get_precision('Account')),
        'sunday_amount': fields.float('Sunday amount', digits_compute=dp.get_precision('Account')),
        'saturday_afternoon_amount': fields.float('Sat. aftno. amount', digits_compute=dp.get_precision('Account')),
        'per_hours': fields.boolean('Per hours')
    }

    _defaults = {
        'holyday_amount': 0.0
    }

analytic_account_invoice_concept_rel()
