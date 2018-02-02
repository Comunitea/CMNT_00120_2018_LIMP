# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2015 Pexego Sistemas Informáticos. All Rights Reserved
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

from osv import osv, fields

class account_move_line(osv.osv):

    _inherit = "account.move.line"

    def _get_invoice_ref(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            invoice_ref = line.invoice and line.invoice.number or False
            if invoice_ref:
                parts = invoice_ref.split("/")
                if len(parts) == 3:
                    invoice_ref = parts[1]
                elif len(parts) == 2:
                    invoice_ref = parts[0]
                else:
                    invoice_ref = False
            res[line.id] = (invoice_ref or line.move_id.name)
        return res

    _columns = {
        'invoice_ref': fields.function(_get_invoice_ref, type="char", method=True, readonly=True, string="Invoice ref")
    }


account_move_line()
