# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Affero GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models

class account_move_line(osv.osv):

    _inherit = "account.move.line"

    _defaults = {
        'manager_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr,uid,uid).context_responsible_id.id or (self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0] or False),
    }

account_move_line()

class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _defaults = {
        'manager_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr,uid,uid).context_responsible_id.id or (self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0] or False),
    }

account_invoice()

class account_analytic_plan_instance_line(osv.osv):

    _inherit = "account.analytic.plan.instance.line"

    _defaults = {
        'manager_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr,uid,uid).context_responsible_id.id or (self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]) and self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])[0] or False),
    }

account_analytic_plan_instance_line()

class account_analytic_account(osv.osv):

    _inherit = "account.analytic.account"

    _defaults = {
        'manager_id': lambda self, cr, uid, context: context.get('c_manager_id',False) or (self.pool.get('res.users').browse(cr,uid,uid).context_responsible_id.id or (self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context) and self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)[0] or False)),
    }

account_analytic_account()

class account_analytic_line(osv.osv):

    _inherit = "account.analytic.line"

    _defaults = {
        'manager_id': lambda self, cr, uid, context: context.get('c_manager_id',False) or (self.pool.get('res.users').browse(cr,uid,uid).context_responsible_id.id or (self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context) and self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)[0] or False)),
    }


account_analytic_line()
