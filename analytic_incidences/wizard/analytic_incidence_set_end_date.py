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


from openerp.osv import osv, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime

class analytic_incidence_set_end_date(osv.osv_memory):

    _name = "analytic.incidence.set.end.date"

    _columns = {
        'end_date': fields.date('End date', required=True)
    }

    def set_end_date(self, cr, uid, ids, context=None):
        if context is None: context = {}
        obj = self.browse(cr, uid, ids[0])

        remuneration_id = context['active_id']
        remuneration_obj = self.pool.get('remuneration').browse(cr, uid, remuneration_id)
        remuneration_obj.write({
            'date_to': obj.end_date
        })

        end_date = (datetime.strptime(remuneration_obj.date, "%Y-%m-%d") + relativedelta(days=-1)).strftime("%Y-%m-%d")
        occupation_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('state', '=', 'active'),('end_type', '=', 'end_date'),('end_date', '=', end_date),('employee_id', '=', remuneration_obj.employee_id.id),('analytic_account_id', '=', remuneration_obj.analytic_account_id.id)])
        if occupation_ids:
            occ_data = self.pool.get('account.analytic.occupation').read(cr, uid, occupation_ids[0], ['duration','date'])
            dat_to = obj.end_date + occ_data['date'][10:]
            date_to = (datetime.strptime(dat_to, "%Y-%m-%d %H:%M:%S") + relativedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
            if occupation_ids:
                other_child_occupations = self.pool.get('account.analytic.occupation').search(cr, uid, [('parent_occupation_id', '=', occupation_ids[0]),('end_date', '=', False)])

                self.pool.get('account.analytic.occupation').copy(cr, uid, occupation_ids[0], default={'date': date_to,
                    'end_date': False,
                    'end_type': 'forever',
                    'state': 'active',
                    'to_invoice' : False,
                    'duration': occ_data['duration'],
                    'parent_occupation_id': occupation_ids[0],
                    'date_deadline': ((datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")) + relativedelta(hours=+occ_data['duration'])).strftime("%Y-%m-%d %H:%M:%S")
                    }, context=context)

            if other_child_occupations:
                self.pool.get('account.analytic.occupation').write(cr, uid, other_child_occupations, {
                    'end_type': 'end_date',
                    'end_date': dat_to
                })

        return {
                'type': 'ir.actions.act_window_close',
            }

analytic_incidence_set_end_date()
