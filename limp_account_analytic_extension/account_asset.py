# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 Pexego Sistemas Informáticos. All Rights Reserved
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

class account_asset(osv.osv):

    _inherit = "account.asset.asset"
    
    
    _columns = {
        'analytic_distribution_id': fields.many2one('account.analytic.plan.instance', 'Analytic distribution')
    }
    
account_asset()

class account_asset_depreciation_line(osv.osv):
    
    _inherit = "account.asset.depreciation.line"
    
    def create_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(account_asset_depreciation_line, self).create_move(cr, uid, ids, context=context)

        for move in self.pool.get('account.move').browse(cr, uid, res):
            for line in move.line_id:
                if line.asset_id and line.asset_id.analytic_distribution_id:
                    line.write({'analytics_id': line.asset_id.analytic_distribution_id.id})
                    
        return res
    
account_asset_depreciation_line()
