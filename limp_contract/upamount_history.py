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

"""Contract upamounts history"""

from osv import osv, fields
import decimal_precision as dp
import time

class limp_contract_upamount_history(osv.osv):
    """Contract upamounts history"""

    _name = "limp.contract.upamount.history"
    _description = "Contract upamount history"
    _order = "date desc"

    _columns = {
        'name': fields.char('Description', size=255, required=True),
        'upamount_percent': fields.float('Upamount percent', digits=(12,3), required=True, readonly=True),
        'previous_amount': fields.float('Previous amount', digits_compute=dp.get_precision('Account'), required=True, readonly=True),
        'new_amount': fields.float('New amount', digits_compute=dp.get_precision('Account'), required=True, readonly=True),
        'date': fields.date('Date', required=True),
        'contract_id': fields.many2one('limp.contract', 'Contract', required=True)
    }

    _defaults = {
        'date': lambda *a: time.strftime("%Y-%m-%d")
    }

limp_contract_upamount_history()

class limp_contract(osv.osv):
    """Add new field to contract"""

    _inherit = 'limp.contract'

    _columns = {
        'upamount_history_ids': fields.one2many('limp.contract.upamount.history', 'contract_id', 'Upamounts history')
    }

limp_contract()
