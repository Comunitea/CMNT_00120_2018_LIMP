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

from osv import osv,fields

class account_analytic_account(osv.osv):
    """Add new field to analytic accounts"""

    _inherit = 'account.analytic.account'

    _columns = {
        'analytic_move_ids': fields.one2many('account.analytic.stock.move', 'analytic_account_id', 'Consumptions')
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'analytic_move_ids': [],
        })

        return super(account_analytic_account, self).copy(cr, uid, id, default, context)
        
    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'analytic_move_ids': [],
        })
        
        return super(account_analytic_account, self).copy_data(cr, uid, id, default, context)

account_analytic_account()
