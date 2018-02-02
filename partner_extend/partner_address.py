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

from osv import fields, osv


class res_partner_address(osv.osv):
    
    _inherit = "res.partner.address"
    
    def name_get(self, cr, user, ids, context=None):
        """
            @param self: The object pointer
            @param cr: the current row, from the database cursor,
            @param user: the current user,
            @param ids: List of partner address’s IDs
            @param context: A standard dictionary for contextual values
        """

        if not len(ids):
            return []
        res = []
        if context is None:
            context = {}
        for r in self.read(cr, user, ids, ['name','zip', 'city', 'partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                addr = "%s %s %s %s" % (r.get('name', '') or '' ,r.get('street', '') or '', r.get('zip', '') \
                                    or '', r.get('city', '') or '')
                res.append((r['id'], addr.strip() or '/'))
        return res
        
        
res_partner_address()
