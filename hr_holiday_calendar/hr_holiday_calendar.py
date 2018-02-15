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

from openerp import models, fields

class HrHolidayCalendar(models.Model):
    """Group of holidays"""

    _name = "hr.holiday.calendar"
    _description = "Holidays calendar"

    holiday_date_start = fields.Date('Start date')
    holiday_date_end = fields.Date('End date')
    name = fields.Char('Name', required=True)
    holiday_ids = fields.One2many('hr.holiday', 'calendar_id', 'Holidays')
    active = fields.Boolean('Active', default=True)
