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
from openerp import models, fields
import time

class ContainerMove(models.Model):
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

    container_id = fields.Many2one('container', 'Container', required=True)
    address_id = fields.Many2one('res.partner', 'Situation', required=True)
    move_type = fields.Selection([('in','In'),('out', 'Out')], 'Move type', required=True, default='in')
    move_date = fields.Datetime('Date', required=True, default=fields.Datetime.now)
    type = fields.Selection(related='container_id.type', store=True, string="Container type")
    responsible_id = fields.Many2one('hr.employee', 'Driver', readonly=True)
