# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

"""History of container moves"""

from osv import osv, fields
import time

class container_move(osv.osv):
    """History of container moves"""

    _name = "container.move"
    _description = "History of container moves"
    _order = "id desc"

    def _get_containers(self, cr, uid, ids, context=None):
        if context is None: context = {}
        result = []
        for obj in self.browse(cr, uid, ids):
            partner_agents_ids = self.pool.get('container.move').search(cr, uid, [('container_id', '=', obj.id)])
            result.extend(partner_agents_ids)
        return result

    _columns = {
        'container_id': fields.many2one('container', 'Container', required=True),
        'address_id': fields.many2one('res.partner.address', 'Situation', required=True),
        'move_type': fields.selection([('in','In'),('out', 'Out')], 'Move type', required=True),
        'move_date': fields.datetime('Date', required=True),
        'type': fields.related('container_id', 'type', selection=[('flat_dumpster4', 'Flat Dumpster 4'), ('flat_dumpster7', 'Flat Dumpster 7'), ('flat_dumpster9', 'Flat Dumpster 9'), ('flat_dumpster12', 'Flat Dumpster 12'),
                        ('flat_dumpster14', 'Flat Dumpster 14'), ('flat_dumpster18', 'Flat Dumpster 18'), ('flat_dumpster30', 'Flat Dumpster 30'), ('trapezoidal4', 'Trapezoidal 4'), ('trapezoidal6', 'Trapezoidal 6'),
                        ('trapezoidal8', 'Trapezoidal 8'), ('other', 'Other')], type="selection", readonly=True, string="Container type",
                        store={'container': (_get_containers, ['type'], 10),
                            'container.move': (lambda self, cr, uid, ids, c={}: ids, ['container_id'], 20)}),
        'responsible_id': fields.many2one('hr.employee', 'Driver', readonly=True)
    }

    _defaults = {
        'move_type': 'in',
        'move_date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    }

container_move()


