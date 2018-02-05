# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos S.L.
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

from openerp import models

class sdd_mandate(models.Model):

    _inherit = "sdd.mandate"

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'unique_mandate_reference': self.pool.get('ir.sequence').get(cr, uid, 'sdd.mandate.reference'),
                        'payment_line_ids': []})

        return super(sdd_mandate, self).copy(cr, uid, id, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'unique_mandate_reference': self.pool.get('ir.sequence').get(cr, uid, 'sdd.mandate.reference'),
                        'state': 'valid',
                        'payment_line_ids': []})
        return super(sdd_mandate, self).copy_data(cr, uid, id, default, context)

sdd_mandate()
