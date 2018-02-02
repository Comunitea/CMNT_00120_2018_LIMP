# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
from time import mktime
import time
from datetime import datetime

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def _get_move_lines_str(self, cr, uid, ids, field_name, args, context=None):
        """returns all move lines related to invoice in string"""
        if context is None: context = {};
        res = {}
        for invoice in self.browse(cr, uid, ids):
            expiration_dates_str = ""
            if invoice.move_id:
                move_lines = [x.id for x in invoice.move_id.line_id]
                move_lines = self.pool.get('account.move.line').search(cr, uid, [('id', 'in', move_lines)], order="date_maturity asc")
                for line in self.pool.get('account.move.line').browse(cr, uid, move_lines):
                    if line.date_maturity:
                        date = time.strptime(line.date_maturity, "%Y-%m-%d")
                        date = datetime.fromtimestamp(mktime(date))
                        date = date.strftime("%d/%m/%Y")
                        if not expiration_dates_str:
                            expiration_dates_str += str(date)
                        else:
                            expiration_dates_str += ", " + str(date)

            res[invoice.id] = expiration_dates_str

        return res

    _columns = {
        'expiration_dates_str': fields.function(_get_move_lines_str, method=True, string='Expiration dates', type="text", readonly=True),
    }

account_invoice()
