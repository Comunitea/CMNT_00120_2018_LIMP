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

class limp_service_picking(models.Model):

    _inherit = "stock.service.picking"

    _columns = {
        'no_quality': fields.boolean('Scont')
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        res = super(limp_service_picking, self).write(cr, uid, ids, vals, context=context)
        if vals.get('no_quality', False):
            for pick in self.browse(cr, uid, ids):
                for line in pick.service_invoice_concept_ids:
                    line.write({'tax_ids': [(6, 0, [])]})

        return res

    def create_concept_lines(self,cr,uid,ids,context=None):
        res = super(limp_service_picking, self).create_concept_lines(cr, uid, ids, context=context)
        for order in self.browse(cr,uid,ids,context=context):
            if order.no_quality:
                for line in order.service_invoice_concept_ids:
                    line.write({'tax_ids': [(6, 0, [])]})

        return res

    def onchange_intercompany(self, cr, uid, ids, intercompany):
        return {'value': {'no_quality': intercompany}}

limp_service_picking()
