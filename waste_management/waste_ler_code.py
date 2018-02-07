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

from openerp.osv import osv, fields

class waste_ler_code(osv.osv):

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            # Be sure name_search is symetric to name_get
            ids = self.search(cr, uid, [('code', 'ilike', name)] + args,
                    limit=limit, context=context)                
            if not ids:
                name = name.split(' / ')[-1]
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    _name = "waste.ler.code"
    _description = "European list of waste"
    _rec_name = "code"

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'code': fields.char('Code', size=10, required=True),
        'dangerous': fields.boolean('Dangerous'),
        'cpa':fields.boolean('cpa'),
        'density': fields.float('Density', digits=(16,3))
    }

    _defaults = {
        'dangerous': False,
        'density': 1.0
    }

waste_ler_code()
