# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos. All Rights Reserved
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
import time
from tools.translate import _

class account_analytic_account_details(osv.osv_memory):
    _name = "account.analytic.account.details"

    _columns = {
        'date1': fields.date('Start of period', required=True),
        'date2': fields.date('End of period', required=True),
        'department_id': fields.many2one('hr.department', 'Department'),
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'manager_id': fields.many2one('hr.employee', 'Responsible', domain=[('responsible', '=', True)]),
        'header': fields.char('Title of report', size=255, required=True),
        'detail': fields.boolean('Show details'),
        'without_pickings': fields.boolean('Without pickings in contract')
    }

    _defaults = {
        'date1': lambda *a: time.strftime('%Y-01-01'),
        'date2': lambda *a: time.strftime('%Y-%m-%d'),
        'header': lambda *a: _('Analytic Details'),
        'without_pickings': lambda *a: True
    }

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'account.analytic.account',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.analytic.account.details.report',
            'datas': datas,
            }

account_analytic_account_details()
