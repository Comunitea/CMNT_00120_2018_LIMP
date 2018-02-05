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

"""Extends contact with new fields"""

from openerp import models, fields
from tools.translate import _

class res_partner_contact(models.Model):
    """Extends contact with new fields"""

    _inherit = "res.partner.contact"

    _columns = {
        'identification_no': fields.char('Identification No', size=32),
        'gender': fields.selection([('male', 'Male'),('female', 'Female')], 'Gender'),
        'ssnid': fields.char('SSN No', size=32, help='Social Security Number'),
        'sinid': fields.char('SIN No', size=32, help="Social Insurance Number"),
        'passport_id':fields.char('Passport No', size=64)
    }
    
    def on_change_identification_nb(self, cr, uid, ids, identification_nb):
        res = {}
        if identification_nb:
            where = [('identification_no','=',identification_nb)]
            if ids:
                where.append(('id','!=',ids[0]))
                
            found = self.search(cr, uid, where)
            if found:
                res['warning'] = {'title': _("Warning!"),
                                    'message': _("Another contact with this identification number")}
                                    
        return res
            

res_partner_contact()
