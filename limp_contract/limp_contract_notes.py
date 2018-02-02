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

from osv import osv, fields
import time

class limp_contract_note(osv.osv):
    
    _name = "limp.contract.note"
    _order = "date desc"
    
    _columns = {
        'date': fields.date('Date', required=True),
        'name': fields.text('Description', required=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'contract_id': fields.many2one('limp.contract', 'Contract')
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'date': lambda *a: time.strftime("%Y-%m-%d")
    }
    
limp_contract_note()
