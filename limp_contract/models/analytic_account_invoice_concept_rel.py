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
from odoo.addons import decimal_precision as dp

class AccountAnalyticInvoiceConcept(models.Model):

    _inherit = "account.analytic.invoice.concept"

    name = fields.Char('Concept', size=255, required=True)


class AnalyticAccountInvoiceConceptRel(models.Model):

    _inherit = "account.analytic.invoice.concept.rel"

    holyday_amount = fields.Float('Holyday amount', digits=dp.get_precision('Account'), default=0.0)
    sunday_amount = fields.Float('Sunday amount', digits=dp.get_precision('Account'))
    saturday_afternoon_amount = fields.Float('Sat. aftno. amount', digits=dp.get_precision('Account'))
    per_hours = fields.Boolean('Per hours')
    total_amount = fields.Float(compute='_compute_total_amount')

    def _compute_total_amount(self):
        for line in self:
            if not line.per_hours:
                if line.freq == 'q':
                    line.total_amount += line.amount * 4
                else:
                    except_months = line._get_except_months()
                    line.total_amount += line.amount * (12 - len(except_months[line.id]))
