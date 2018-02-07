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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import datetime
import time

class account_analytic_occupation(osv.osv):
    """Object to manage employee's occupations in analytic accounts"""

    _name = "account.analytic.occupation"
    _inherit = "calendar.event"

    def _get_toshow_end_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        for occupation in self.read(cr, uid, ids, ['end_date', 'recurrency', 'date_deadline']):
            if occupation['recurrency']:
                res[occupation['id']] = occupation['end_date']
            else:
                res[occupation['id']] = occupation['date_deadline'][:10]
        return res

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Account'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'partner_id': fields.related('analytic_account_id', 'partner_id', string="Customer", type="many2one", relation="res.partner", readonly=True),
        'to_invoice' : fields.boolean('To invoice'),
        'exception_date': fields.date('Exception Date', states={'done': [('readonly', True)]},),
        'exception_duration': fields.float('Duration', states={'done': [('readonly', True)]}),
        'old': fields.boolean('Old', states={'done': [('readonly', True)]}),
        'toshow_end_date': fields.function(_get_toshow_end_date, method=True, string='End date', readonly=True, type="date"),
        'timetable_text': fields.text('Timetable'),
        'value_diff': fields.float('Value Diff')
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
        'to_invoice' : True,
        'value_diff': 0.0
    }

    def search(self, cr, uid, args, offset=0, limit=500, order=None,context=None, count=False):
        """increases search limit to 500"""
        limit = 500
        #if not limit:
        #    limit = 500
        if context is None: context = {}

        return super(account_analytic_occupation, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_get(self, cr, uid, ids, context=None):
        """return other name if it is contract line"""
        if context is None:
            context = {}
        if not ids:
            return []
        res = []

        for obj in self.browse(cr, uid, ids, context=context):
            name = self.read(cr,uid,ids,['analytic_account_id'])[0]
            res.append((obj.id, name['analytic_account_id'][1]))
        return res

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        if not context:
            context = {}
        if context.get('is_contract', False):
            occ = self.browse(cr, uid, id)
            if occ.toshow_end_date:
                return {}
        return super(account_analytic_occupation, self).copy_data(cr, uid, id, default, context)

    def add_exception_date(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        occupation = self.browse(cr,uid,ids[0],context)
        if not occupation.exception_date:
            raise osv.except_osv(_('Error'), _('Field Exception date empty'))
        ex_date = time.strftime("%Y%m%dT%H%M%S",time.strptime(occupation.exception_date + occupation.date[10:], "%Y-%m-%d %H:%M:%S"))
        except_date = occupation.exdate and occupation.exdate +','+ex_date or ex_date
        occupation.write({'exdate' : except_date, 'exception_date': False, 'exception_duration': 0.0})
        if occupation.exception_duration != 0:
            vals = {
                'occupation_name_id' : occupation.occupation_name_id.id,
                'employee_id' : occupation.employee_id.id,
                'date': occupation.exception_date + occupation.date[10:],
                'duration': occupation.exception_duration,
                'to_invoice': False,
                'parent_occupation_id': occupation.id,
                'analytic_account_id' : occupation.analytic_account_id and occupation.analytic_account_id.id or False,
                'company_id' : occupation.company_id and occupation.company_id.id or False,
                'state_id':  occupation.state_id and  occupation.state_id.id or False,
                'location_id': occupation.location_id and  occupation.location_id.id or False,
                'partner_id':  occupation.partner_id and occupation.partner_id.id or False,
                'delegation_id': occupation.delegation_id and occupation.delegation_id.id or False,
                'department_id': occupation.department_id and occupation.department_id.id or False,
            }
            self.create(cr,uid,vals,context)
        return True
account_analytic_occupation()
