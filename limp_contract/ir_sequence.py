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

"""Add delegation to sequence model"""

from osv import osv, fields

class ir_sequence(osv.osv):
    """Add delegation to sequence model"""

    _inherit = "ir.sequence"

    _columns = {
        'delegation_id': fields.many2one('res.delegation', 'Delegation')
    }

    def search_by_delegation(self, cr, uid, code, delegation, context=None):
        """search sequence by code and delegation"""
        if context is None: context = {}
        company_id = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)['company_id'][0] or None

        cr.execute('''SELECT id
                      FROM ir_sequence
                      WHERE code='%s'
                       AND active=true
                       AND (company_id = %s or company_id is NULL)
                       AND (delegation_id = %s or delegation_id is NULL)
                      ORDER BY company_id, id
                      FOR UPDATE NOWAIT''' % (code, company_id, delegation))
        res = cr.dictfetchone()

        return res and res['id'] or False

    def get_by_delegation(self, cr, uid, code, delegation):
        """obtains corect sequence by delegation and code"""
        res = self.search_by_delegation(cr, uid, code, delegation)
        
        if res:
            return self.get_id(cr, uid, res)
        return self.get(cr, uid, code)


ir_sequence()
