# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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

import time
from openerp import models, fields

class print_acceptance_document_report(models.TransientModel):

    _name = "print.acceptance.document.report"

    _columns = {
        'building_site_id': fields.many2one('building.site.services', 'Building Site / Service', required=True),
        'waste_id': fields.many2one('waste.ler.code', 'LER', required=True)
    }

    def print_report(self, cr, uid, ids, context=None):
        """prints report"""
        if context is None:
            context = {}

        obj = self.browse(cr, uid, ids[0])
        acceptance_ids = self.pool.get('acceptance.document').search(cr, uid, [('building_site_id', '=', obj.building_site_id.id),('waste_id', '=', obj.waste_id.id)])
        if acceptance_ids:
            data = self.pool.get('acceptance.document').read(cr, uid, acceptance_ids[0])
            accept_ids = [acceptance_ids[0]]
        else:
            admission_seq = self.pool.get('ir.sequence').get(cr, uid, 'acceptance_document')
            new_waste = self.pool.get('acceptance.document').create(cr, uid, {
                                                                        'building_site_id': obj.building_site_id.id,
                                                                        'waste_id': obj.waste_id.id,
                                                                        'number': admission_seq
                                                                    })
            data = self.pool.get('acceptance.document').read(cr, uid, new_waste)
            accept_ids = [new_waste]

        datas = {'ids': accept_ids}
        datas['model'] = 'acceptance.document'
        datas['form'] = data
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'acceptance_document',
            'datas': datas,
        }

print_acceptance_document_report()
