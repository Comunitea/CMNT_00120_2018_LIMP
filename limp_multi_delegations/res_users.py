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

"""Add new delegation relationship to users"""

from openerp.osv import osv, fields

class res_users(osv.osv):
    """Add new delegation relationship to users"""

    _inherit = "res.users"

    _columns = {
        'delegation_ids': fields.many2many('res.delegation', 'res_delegation_users_rel', 'user_id', 'delegation_id', 'Delegations'),
        'context_delegation_id': fields.many2one('res.delegation', 'Delegation')
    }

res_users()