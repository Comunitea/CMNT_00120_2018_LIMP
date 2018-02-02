# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

"""
ICS Files importation Wizard
"""

from osv import osv, fields
import base64

class import_ics_wzd(osv.osv_memory):
    """ Object to import ICS Files """

    _name = "import.ics.wzd"
    _description = "ICS Files importation Wizard"

    _columns = {
        'file': fields.binary('ICS file to import', required = True),
        'name': fields.char('Description', size=255, required = True),
        'state': fields.selection([('first', 'First'),('second', 'Second')], 'State', readonly=True),
        'scope': fields.selection([('local', 'Local'),('provintial', 'Provintial'), ('state', 'State'), ('autonomic', 'Autonomic'), ('national', 'National')], 'Scope'),
        'country_id': fields.many2one('res.country', 'Country'),
        'state_id': fields.many2one('res.country.state', 'State')
    }

    _defaults = {
        'state': 'first',
        'scope': 'national'
    }
    
    def import_file(self, cr, uid, ids, context=None):
        """ Import method """
        if context is None: context = {}

        holiday_facade = self.pool.get('hr.holiday')
        holiday_calendar_facade = self.pool.get('hr.holiday.calendar')
        obj = self.browse(cr, uid, ids)[0]

        # Lectura del archivo ICS
        holidays = []
        flag = False
        file = base64.decodestring(obj.file)

        try:
            unicode(file, 'utf8')
        except Exception, e:
            file = unicode(file, 'iso-8859-1').encode('utf-8')
            
        for line in file.split("\n"):
            if len(line) == 0:
                continue
           
            if (line[0:12]=='BEGIN:VEVENT'): # Holiday begin statement
                holiday = []
                flag = True
            elif ((line[0:7]=='DTSTART') and flag): #Holiday date start
                startDate = line[line.find(":")+1:len(line)-1]
                holiday.insert(0, startDate)
            elif ((line[0:7]=='SUMMARY') and flag):#Add holiday description
                holiday.append(line[8:(len(line)-1)])
            elif ((line[0:10]=='END:VEVENT') and flag==1): #Holiday end statement
                flag = False
                holidays.append(holiday)

        calendar_id = holiday_calendar_facade.create(cr, uid, {'name': obj.name}, context=context)
        begin_cal_date = '29991231'
        end_cal_date = '18991231'

        for holiday in holidays:
            if (begin_cal_date > holiday[0]):
                begin_cal_date = holiday[0]

            if (end_cal_date < holiday[0]):
                end_cal_date = holiday[0]

            holiday_facade.create(cr, uid, {
                        'holiday_date': holiday[0],
                        'name': holiday[1],
                        'scope': obj.scope,
                        'country_id': obj.country_id and obj.country_id.id or False,
                        'state_id': obj.state_id and obj.state_id.id or False,
                        'calendar_id': calendar_id
                    }, context=context)

        holiday_calendar_facade.write(cr, uid, [calendar_id], {
                                                        'holiday_date_start': begin_cal_date,
                                                        'holiday_date_end': end_cal_date
                                                        })

        self.write(cr, uid, ids, {'state': 'second'})

        return True

import_ics_wzd()