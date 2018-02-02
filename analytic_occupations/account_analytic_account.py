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

"""Adds occupation fiels to analytic account's columns"""

from osv import osv,fields
import time

class account_analytic_account(osv.osv):
    """Adds occupation fiels to analytic account's columns"""

    _inherit = "account.analytic.account"

    _columns = {
        'occupation_ids': fields.one2many('account.analytic.occupation', 'analytic_account_id', 'Occupations'),
        'active_occupation_ids': fields.one2many('account.analytic.occupation', 'analytic_account_id', 'Active occupations', domain=[('state', 'in', ('draft','active','replacement')),('old','=',False)]),
        'unactive_occupation_ids': fields.one2many('account.analytic.occupation', 'analytic_account_id', 'Unactive occupations', domain=['|',('state', 'not in', ('draft','active','replacement')),('old','=',True)])
    }

account_analytic_account()
