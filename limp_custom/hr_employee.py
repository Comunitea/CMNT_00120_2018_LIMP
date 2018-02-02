# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class hr_employee(osv.osv):
    
    _inherit = 'hr.employee'
    
    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'colege_num': fields.char('Colege number', size=64),
        'private_address': fields.char('Private address', size=255)
    }
    
    _defaults = {
        'delegation_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).context_delegation_id.id
    }
    
hr_employee()
