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

"""Extends this object to add state field"""

from openerp import models, fields
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime

def base_calendar_id2real_id(base_calendar_id=None, with_date=False):
    """
    This function converts virtual event id into real id of actual event
    @param base_calendar_id: Id of calendar
    @param with_date: If value passed to this param it will return dates based on value of withdate + base_calendar_id
    """

    if base_calendar_id and isinstance(base_calendar_id, (str, unicode)):
        res = base_calendar_id.split('-')

        if len(res) >= 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime("%Y-%m-%d %H:%M:%S", \
                                 time.strptime(res[1], "%Y%m%d%H%M%S"))
                start = datetime.strptime(real_date, "%Y-%m-%d %H:%M:%S")
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime("%Y-%m-%d %H:%M:%S"))
            return int(real_id)

    return base_calendar_id and int(base_calendar_id) or base_calendar_id

class account_analytic_occupation(models.Model):
    """Extends this object to add state field"""

    _inherit = 'account.analytic.occupation'

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('active', 'Active'), ('incidence', 'Based of incidence'), ('replaced', 'Replaced'), ('replacement', 'Replacement'), ('cancelled', 'Cancelled')], 'State', readonly=True),
        'incidence_id': fields.many2one('hr.laboral.incidence', 'Incidence', readonly=True),
        'remuneration_id': fields.many2one('remuneration', 'Remuneration', readonly=True),
        'parent_occupation_id': fields.many2one("account.analytic.occupation", 'Parent')
    }

    _defaults = {
        'state': 'active',
    }

    def get_duration_to_invoice(self, cr, uid, ids, context=None):
        if context is None: context = {}
        ids = isinstance(ids, (int,long,str,unicode)) and [ids] or ids

        occupation_ids = map(lambda x: base_calendar_id2real_id(x), ids)
        occupation_ids = list(set(occupation_ids))
        if occupation_ids:
            occupation = self.browse(cr, uid, occupation_ids[0])
            if occupation.to_invoice:
                return occupation.duration
            elif occupation.parent_occupation_id:
                return self.get_duration_to_invoice(cr, uid, occupation.parent_occupation_id.id)
            else:
                return 0.0
        return 0.0

    def set_active(self, cr, uid, ids, context=None):
        """Set active state"""
        if context is None: context = {}

        self.write(cr, uid, ids, {'state': 'active', 'edit_all': True})
        self.write(cr, uid, ids, {'edit_all': False})

        return True
    def write(self, cr, uid, ids, vals, context=None):

        if context is None: context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        if vals.get('end_type', False):
            if vals['end_type'] == 'forever':
                for occupation_id in self.browse(cr, uid, ids):
                    if occupation_id <> False:
                        vals['end_date'] = False

        return super(account_analytic_occupation, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):

        if context is None: context = {}

        if (vals.get('state') and vals['state'] == 'draft') or not vals.get('state'):
            vals['state'] = 'active'

        return super(account_analytic_occupation, self).create(cr, uid, vals, context=context)
account_analytic_occupation()
