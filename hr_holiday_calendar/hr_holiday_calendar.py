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

"""Group of holidays"""

from openerp.osv import osv, fields

class hr_holiday_calendar(osv.osv):
    """Group of holidays"""

    _name = "hr.holiday.calendar"
    _description = "Holidays calendar"

    _columns = {
        'holiday_date_start': fields.date('Start date'),
        'holiday_date_end': fields.date('End date'),
        'name': fields.char('Name', size=255, required=True),
        'holiday_ids': fields.one2many('hr.holiday', 'calendar_id', 'Holidays'),
        'active': fields.boolean('Active')
    }

    _defaults = {
        'active': True
    }

hr_holiday_calendar()
