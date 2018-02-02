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

"""wizard to sign contract"""

from osv import osv, fields
import time

class limp_contract_signature(osv.osv_memory):
    """wizard to sign contract"""

    _name = 'limp.contract.signature'
    _description = "Contract signature"

    _columns = {
        'contract_date' : fields.date('Signature date', required=True),
    }

    _defaults = {
        'contract_date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def set_signature(self, cr, uid, ids, context=None):
        """Adds signature date to contract and moves forward the contract's state"""
        obj = self.browse(cr, uid, ids[0])

        contract = self.pool.get('limp.contract').browse(cr, uid, context['active_id'])
        self.pool.get('limp.contract').write(cr, uid, contract.id, {
                'signature_date': obj.contract_date,
                'state': 'open'
            })

        self.pool.get('account.analytic.account').write(cr, uid, contract.analytic_account_id.id, {'state': 'open'})

        return { 'type': 'ir.actions.act_window_close' }

limp_contract_signature()