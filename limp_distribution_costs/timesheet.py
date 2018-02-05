# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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

from openerp import models, fields
import decimal_precision as dp
import time
from tools.translate import _


class timesheet(models.Model):
    _name = 'timesheet'

    def _get_pending_qty(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for tsobj in self.browse(cr, uid, ids):
            res[tsobj.id] = {}
            res[tsobj.id]['pending_qty'] = (tsobj.extra_hours * tsobj.price_hours) + (tsobj.hours * tsobj.price_hours) + tsobj.quantity
            res[tsobj.id]['pending_distribute_qty'] = res[tsobj.id]['pending_qty'] - tsobj.effective - tsobj.fix_qty

        return res

    def _get_total_hours(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for tsobj in self.browse(cr, uid, ids):
            res[tsobj.id] = tsobj.ss_hours + tsobj.ss_no_hours

        return res

    _columns = {
        'name': fields.char('Name', size=12),
        'date': fields.date('Date', required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Analytic account'),
        'hours': fields.float('Hours',digits=(12,2), required=True),
        'contract': fields.boolean('Contract'),
        'fix_qty': fields.float('Fix Qty.', digits_compute=dp.get_precision('Account')),
        'quantity': fields.float('Qty.', digits_compute=dp.get_precision('Account')),
        'extra_hours': fields.float('Extra Hours',digits=(4,2)),
        'price_hours': fields.float('Price Hours',digits=(4,2)),
        'effective': fields.float('Effective',digits=(4,2)),
        'done': fields.boolean('Done'),
        'paid': fields.boolean('Paid'),
        'paid_date': fields.date('Paid date'),
        'ss_hours': fields.float('SS hours', digits=(4,2)),
        'ss_no_hours': fields.float('No ss hours', digits=(4,2)),
        'total_hours': fields.function(_get_total_hours, method=True, string="Total hours", readonly=True, type="float"),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'pending_qty': fields.function(_get_pending_qty, method=True, string='Quantity to Distribute', digits=(12,2), readonly=True, type="float", multi="pending",
                                       store={'timesheet': (lambda self, cr, uid, ids, c={}: ids, ['extra_hours','price_hours','hours','quantity','effective','fix_qty'], 10)}),
        'pending_distribute_qty': fields.function(_get_pending_qty, digits=(12,2), method=True, string="Pending Quantity", type="float", readonly=True, multi="pending",
                                                  store={'timesheet': (lambda self, cr, uid, ids, c={}: ids, ['extra_hours','price_hours','hours','quantity','effective','fix_qty'], 10)}),
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'responsible_id': fields.many2one('hr.employee' ,'Responsible', domain=[('responsible', '=', True)]),
        'description': fields.char('Description', size=255),
        'old': fields.boolean('Old'),
        'employee_delegation_id': fields.many2one('res.delegation', 'Employee Delegation'),
        'employee_department_id': fields.many2one('hr.department', 'Employee Department'),
        'create_uid': fields.many2one('res.users', 'Creator', readonly=True)
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'timesheet'),
        'company_id': lambda self, cr, uid, context: context.get('company_id', False) or self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id and self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id or False,
    }

    def onchange_hours(self,cr,uid,ids,effective,fix_qty,hours,price_hours,extra_hours,quantity,context=None):
        res = self.onchange_qtys(cr,uid,ids,effective,fix_qty,hours,price_hours,extra_hours,quantity,context=context)
        if hours:
            res['value']['contract'] = True
            res['value']['done'] = True
            res['value']['paid'] = True
        else:
            res['value']['contract'] = False
            res['value']['done'] = False
            res['value']['paid'] = False
        return res


    def onchange_qtys(self,cr,uid,ids,effective,fix_qty,hours,price_hours,extra_hours,quantity,context=None):
        res = {'value': {}}
        pending_qty = (extra_hours * price_hours) + (hours * price_hours) + quantity
        res['value']['pending_qty'] = pending_qty
        calc = pending_qty - effective - fix_qty
        res['value']['pending_distribute_qty'] = calc
        return res

    def on_change_analytic_id(self, cr, uid, ids, analytic_acc_id=False, context=None):
        res = {'value': {}}
        if not analytic_acc_id:
            res['value'] = {
                'delegation_id': False,
                'department_id': False,
                'responsible_id': False
            }
        else:
            analytic = self.pool.get('account.analytic.account').browse(cr, uid, analytic_acc_id)
            res['value'] = {
                'delegation_id': analytic.delegation_id.id,
                'department_id': analytic.department_id.id,
                'responsible_id': analytic.manager_id.id
            }

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        if vals.get('hours', 0.0) and not vals.get('paid', False):
            vals['paid'] = True
            vals['contract'] = True
        if vals.get('fix_qty', False) and vals.get('done', False) and not vals.get('paid', False):
            vals['paid'] = True
            vals['contract'] = True
        if vals.get('paid', False):
            vals['paid_date'] = time.strftime("%Y-%m-%d")
        if vals.get('hours', 0.0) and not vals.get('ss_hours', 0.0):
            vals['ss_hours'] = vals['hours']
        if vals.get('employee_id', False):
            employee_id = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'])
            vals['employee_delegation_id'] = employee_id.delegation_id.id
            vals['employee_department_id'] = employee_id.department_id.id

        return super(timesheet, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if vals.get('hours', 0.0) and not vals.get('paid', False):
            vals['paid'] = True
            vals['contract'] = True
        if vals.get('fix_qty', False) and vals.get('done', False) and not vals.get('paid', False):
            vals['paid'] = True
            vals['contract'] = True
        if vals.get('paid', False) and not vals.get('paid_date', False):
            vals['paid_date'] = time.strftime("%Y-%m-%d")
        if vals.get('hours', 0.0) and not vals.get('ss_hours', 0.0):
            vals['ss_hours'] = vals['hours']
        if vals.get('employee_id', False):
            employee_id = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'])
            vals['employee_delegation_id'] = employee_id.delegation_id.id
            vals['employee_department_id'] = employee_id.department_id.id
        #~ if uid != 1 and vals:
            #~ for tim in self.browse(cr, uid, ids):
                #~ if tim.create_uid.id != uid:
                    #~ user = self.pool.get('res.users').browse(cr, uid, uid)
                    #~ if not user.laboral:
                        #~ raise osv.except_osv(_('Error'), _('Cannot update this timesheet, because you are not the creator or admin.'))
        for line in self.browse(cr, uid, ids):
            if 'hours' in vals and not vals['hours'] and line.hours:
                vals['contract'] = False
                vals['paid'] = False
                vals['done'] = False
                vals['paid_date'] = False

        return super(timesheet, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None: context = {}
        if uid != 1:
            for tim in self.browse(cr, uid, ids):
                if tim.create_uid.id != uid:
                    raise osv.except_osv(_('Error'), _('Cannot delete this timesheet, because you are not the creator or admin.'))
        return super(timesheet, self).unlink(cr, uid, ids, context=context)

timesheet()
