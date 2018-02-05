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

"""Add new object as dimension of multi-company rules"""

from openerp import models, fields
from tools.translate import _

class res_delegation(models.Model):
    """Add new object as dimension of multi-company rules"""

    _name = "res.delegation"
    _description = "Delegation"

    _columns = {
        'name': fields.char('Delegation', size=32, required=True),
        'code': fields.char('Code', size=8),
        'description': fields.text('Description'),
        'parent_id': fields.many2one('res.delegation', 'Parent delegation'),
        'child_ids': fields.one2many('res.delegation', 'parent_id', 'Child delegations'),
        'user_ids': fields.many2many('res.users', 'res_delegation_users_rel', 'delegation_id', 'user_id', 'Related users'),
        'address_id': fields.many2one('res.partner','Delegation Address')
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        """avoid recursion in delegations"""
        if context is None:
            context = {}

        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from res_delegation where id IN %s', (tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, _('Error! You can not create recursive delegations.'), ['parent_id'])
    ]

res_delegation()
