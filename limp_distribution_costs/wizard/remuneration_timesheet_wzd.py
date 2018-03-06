# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $ Javier Colmenero Fernández $
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

from odoo import models, fields
import time
import calendar
import datetime

class RemunerationTimesheetWzd(models.TransientModel):

    _name = "remuneration.timesheet.wzd"

    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')],
       'Month', required = True)
    year = fields.Integer('Year', required=True, default=lambda r: int(time.strftime("%Y")))

    def set_timesheet_lines(self):
        part_date = str(self.year)+'-'+str(self.month)
        first_day, last_day = calendar.monthrange(int(self.year),int(self.month))
        start_date = part_date+'-01'
        end_date = part_date+'-'+str(last_day)

        rem_ids = self.env["remuneration"].search(['|',('date_to','>=',start_date),('date_to','=',False),('date','<=',end_date),('effective','!=',0.0)])
        for rem_id in rem_ids:
            if not rem_id.parent_id or rem_id.employee_id != rem_id.parent_id.employee_id:
                remu_periods = rem_id.get_periods_remuneration(start_date, end_date)
                for period in remu_periods:
                    rem_start_date, rem_end_date = period.split('#')
                    date1_format = datetime.datetime.strptime((rem_start_date + ' 00:00:00'),"%Y-%m-%d %H:%M:%S")
                    date2_format = datetime.datetime.strptime((rem_end_date + ' 23:59:59'),"%Y-%m-%d %H:%M:%S")
                    #calculamos el número de días en el periodo
                    if rem_end_date[8:10] == str(last_day):
                        days_diff = 30 - int(rem_end_date[8:10]) + 1
                    else:
                        days_diff = 1
                    days = (date2_format - date1_format).days
                    days += days_diff

                    for remuneration_id in remu_periods[period]:
                        rem = self.env["remuneration"].browse(remuneration_id)
                        effective_amount = round((rem.effective * days) / 30.0, 2)
                        data = {
                            'name': 'Rem. ' + rem.name,
                            'employee_id': rem.employee_id and rem.employee_id.id or False,
                            'effective': effective_amount,
                            'quantity': effective_amount,
                            'date': end_date,
                            'hours': 0.00,
                            'done': True,
                            'department_id': (rem.analytic_account_id and rem.analytic_account_id.department_id) and rem.analytic_account_id.department_id.id or False,
                            'delegation_id': (rem.analytic_account_id and rem.analytic_account_id.delegation_id) and rem.analytic_account_id.delegation_id.id or False,
                            'responsible_id': (rem.analytic_account_id and rem.analytic_account_id.custom_manager_id) and rem.analytic_account_id.custom_manager_id.id or False
                        }
                        if rem.analytic_account_id:
                            data.update({'analytic_id': rem.analytic_account_id.id})
                            self.env["timesheet"].create(data)
                        elif rem.analytic_distribution_id:
                            for line in rem.analytic_distribution_id.account_ids:
                                data.update({
                                    'effective': round(line.rate and effective_amount * (line.rate / 100.0) or line.fix_amount, 2),
                                    'quantity': round(line.rate and effective_amount * (line.rate / 100.0) or line.fix_amount, 2),
                                    'analytic_id': line.analytic_account_id.id,
                                    'department_id': line.department_id and line.department_id.id or False,
                                    'delegation_id': line.delegation_id and line.delegation_id.id or False,
                                    'responsible_id': line.custom_manager_id and line.custom_manager_id.id or False
                                })
                                self.env["timesheet"].create(data)


        return {'type' : 'ir.actions.act_window_close'}
