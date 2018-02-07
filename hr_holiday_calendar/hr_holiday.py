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

"""Represents an holiday"""

from osv import osv, fields

class hr_holiday(osv.osv):
    """Represents an holiday"""

    _name = 'hr.holiday'
    _description = "Holiday"

    _columns = {
        'calendar_id': fields.many2one('hr.holiday.calendar', 'Calendar'),
        'holiday_date': fields.date('Date'),
        'name': fields.char('Name', size=128),
        'location_id': fields.many2one('city.council', 'Council'),
        'scope': fields.selection([('local', 'Local'), ('state', 'State'), ('autonomic', 'Autonomic'), ('national', 'National')], 'Scope'),
        'country_id': fields.many2one('res.country', 'Country'),
        'state_id': fields.many2one('res.country.state', 'State'),
        #'region_id': fields.many2one('res.country.region', 'Autonomous') MIGRACION: Region eliminado
    }

    _defaults = {
        'scope': 'national'
    }
    def get_holidays_dates(self, cr, uid, ids, location_id=False, state_id=False, region_id=False,context=None):
        """returns holidays separated by semicolon for using rules"""
        if context is None: context = {}
        if isinstance(ids, (long, int)):
            ids = [ids]
        exdate = []
        res = {}
        ids_country = []
        ids_country_region = []
        ids_country_region_state = []
        ids_country_region_state_city = []
        for employee in self.browse(cr, uid, ids):
            if state_id:
                state = self.pool.get('res.country.state').browse(cr, uid, state_id)
                if state:
                    ids_country = self.pool.get('hr.holiday').search(cr, uid, [('country_id','=',state.country_id.id),('region_id','=',False),('state_id','=',False),('location_id','=',False)])
                    if region_id:
                        ids_country_region = self.pool.get('hr.holiday').search(cr, uid, [('country_id','=',state.country_id.id),('region_id','=',region_id),('state_id','=',False),('location_id','=',False)])
                        ids_country_region_state = self.pool.get('hr.holiday').search(cr, uid, [('country_id','=',state.country_id.id),('region_id','=',region_id),('state_id','=',state_id),('location_id','=',False)])
                        ids_country_region_state_city = self.pool.get('hr.holiday').search(cr, uid, [('country_id','=',state.country_id.id),('region_id','=',region_id),('state_id','=',state_id),('location_id','=',location_id)])


            if ids_country:
                for line_c in ids_country:
                    obj = self.pool.get('hr.holiday').browse(cr, uid, line_c)
                    exdate.append(obj.holiday_date)
            if ids_country_region:
                for line_cr in ids_country_region:
                    obj = self.pool.get('hr.holiday').browse(cr, uid, line_cr)
                    exdate.append(obj.holiday_date)
            if ids_country_region_state:
                for line_crs in ids_country_region_state:
                    obj = self.pool.get('hr.holiday').browse(cr, uid, line_crs)
                    exdate.append(obj.holiday_date)
            if ids_country_region_state_city:
                for line_crsc in ids_country_region_state_city:
                    obj = self.pool.get('hr.holiday').browse(cr, uid, line_crsc)
                    exdate.append(obj.holiday_date)

            if exdate:
                res[employee.id] = list(set(exdate))
            else:
                res[employee.id] = []

        return res


hr_holiday()
