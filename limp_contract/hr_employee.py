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

"""Add new method to get employee's holidays"""

from openerp import models, fields

class hr_employee(models.Model):

    _inherit = "hr.employee"
    _columns = {
        'title': fields.char('Title', size=255)
    }
    def get_holidays_dates(self, cr, uid, ids, context=None):
        """returns holidays separated by semicolon for using rrules"""
        if context is None: context = {}

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = {}

        for employee in self.browse(cr, uid, ids):
            exdate = []
            for calendar in employee.calendar_ids:
                for holiday in calendar.holiday_ids:
                    exdate.append(holiday.holiday_date)

            res[employee.id] = list(set(exdate))

        return res

hr_employee()
